//! Parser for the DLL collection's shipped C headers.
//!
//! The grammar is deliberately small — exactly what the kits' headers
//! use. It was first surveyed against NotifyKit, WatchKit and SignKit,
//! and extended 2026-11-12 after a full survey of all 33 shipped
//! headers found real types the first survey missed (`int64_t`,
//! `uint8_t`, `size_t`, `double`, scalar out-pointers, byte buffers,
//! function-pointer typedefs and one callbacks struct). The rule is
//! unchanged: a type is mapped only when its mapping is exact, and
//! anything else is a hard error naming the token.
//!
//! - Prototypes look like `RET prefix_name(params);`, optionally led
//!   by an export macro (`NO_API`, `WA_API`, `SG_API` — any all-caps
//!   token ending in `_API`), and may span several lines.
//! - Comments (`/* ... */` and `// ...`) and preprocessor lines are
//!   ignored. `enum` and opaque `typedef struct Name Name;` statements
//!   are skipped; the `extern "C"` wrapper is unwrapped.
//! - Function-pointer typedefs (`typedef RET (*Name)(params);`) are
//!   collected, and parameters of that type are callbacks.
//! - Concrete structs (`typedef struct Name { fields } Name;`) are
//!   collected with their fields, and `Name *` parameters refer to
//!   them (ProviderKit's callbacks struct is the one real case).
//! - Types: `void`, `int`, `unsigned int`, `uint32_t`, `uint64_t`,
//!   `int64_t`, `uint8_t`, `size_t`, `float`, `double`,
//!   `const char *`, `char *`, `char **`, `void *`, `const void *`,
//!   opaque handles `Name *` / `Name **` / `const Name *` where `Name`
//!   is a capitalized typedef'd struct name, scalar pointers
//!   `T *` / `T **` / `const T *` for the numeric types above, and
//!   callback and struct types as described.
//! - A scalar `T *` parameter is an out-parameter when its name says
//!   so (`out`, `out_*`, `*_out`, `found`) and a by-value buffer
//!   pointer otherwise (`p` in `xx_free_buffer(uint8_t *p, ...)`) —
//!   the distinction is decided by the name the header itself gives,
//!   recorded on [`Param::is_out_param`], never by the pointed-to
//!   type alone.
//! - Anything else is a hard error naming the offending token. A type
//!   mapping is never guessed: a guessed signature compiles, loads,
//!   and then lies at runtime, which is the failure this tool exists
//!   to prevent (hand-copied P/Invoke signatures have done exactly
//!   that in this collection's history).

/// One C type from the pinned grammar.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CType {
    Void,
    Int,
    /// `unsigned int`
    UInt,
    /// `uint32_t`
    U32,
    /// `uint64_t`
    U64,
    /// `int64_t`
    I64,
    /// `uint8_t`
    U8,
    /// `size_t`
    SizeT,
    /// `float`
    F32,
    /// `double`
    F64,
    /// `const char *`
    ConstCharPtr,
    /// `char *`
    CharPtr,
    /// `char **`
    CharPtrPtr,
    /// `void *`
    VoidPtr,
    /// `const void *`
    ConstVoidPtr,
    /// `Name *` — an opaque handle.
    HandlePtr(String),
    /// `Name **` — an out-pointer for a handle.
    HandlePtrPtr(String),
    /// `const Name *` — a read-only opaque handle.
    ConstHandlePtr(String),
    /// `T *` for a numeric `T` — an out-parameter or a by-value
    /// buffer pointer; [`Param::is_out_param`] carries the header's
    /// own naming signal.
    ScalarPtr(Box<CType>),
    /// `const T *` for a numeric `T` — a read-only buffer.
    ConstScalarPtr(Box<CType>),
    /// `T **` for a numeric `T` — an out-pointer for a buffer.
    ScalarPtrPtr(Box<CType>),
    /// A function-pointer typedef used as a parameter type.
    Callback(String),
    /// `T[N]` — a fixed-size array field inside a concrete struct
    /// (the element is a scalar; a `char` element is carried as
    /// `U8`, the collection's byte convention).
    Array(Box<CType>, usize),
    /// `Name *` — a concrete struct collected from the header.
    StructPtr(String),
    /// `const Name *` — a read-only concrete struct.
    ConstStructPtr(String),
}

impl CType {
    /// True for the two string-return types (`char *` caller-owned,
    /// `const char *` borrowed).
    pub fn is_string_return(&self) -> bool {
        matches!(self, CType::CharPtr | CType::ConstCharPtr)
    }

    /// The handle type name, if this type is an opaque handle.
    pub fn handle_name(&self) -> Option<&str> {
        match self {
            CType::HandlePtr(n) | CType::HandlePtrPtr(n) | CType::ConstHandlePtr(n) => Some(n),
            _ => None,
        }
    }
}

/// One named function parameter.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Param {
    pub name: String,
    pub ty: CType,
}

impl Param {
    /// True when this parameter is a scalar out-parameter. The
    /// collection's headers name out-parameters `out`, `out_*`,
    /// `*_out` or `found`; every other scalar `T *` parameter is a
    /// by-value buffer pointer (the `p` in `xx_free_buffer`).
    /// Generators use this to choose `out T` vs `IntPtr` in C#; the
    /// Rust mapping is a raw pointer either way, so it never needs
    /// the distinction.
    pub fn is_out_param(&self) -> bool {
        matches!(self.ty, CType::ScalarPtr(_))
            && (self.name == "out"
                || self.name == "found"
                || self.name.starts_with("out_")
                || self.name.ends_with("_out"))
    }
}

/// One parsed prototype.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Function {
    pub name: String,
    pub ret: CType,
    pub params: Vec<Param>,
}

/// A function-pointer typedef: `typedef RET (*Name)(params);`.
/// Parameter names may be empty (C allows unnamed parameters in a
/// typedef); generators synthesize positional names where a target
/// language requires them.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CallbackDef {
    pub name: String,
    pub ret: CType,
    pub params: Vec<Param>,
}

/// A concrete struct: `typedef struct Name { fields } Name;`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StructDef {
    pub name: String,
    pub fields: Vec<Param>,
}

/// A parsed header: the prototypes, callback typedefs and concrete
/// structs, each in declaration order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Header {
    pub functions: Vec<Function>,
    pub callbacks: Vec<CallbackDef>,
    pub structs: Vec<StructDef>,
}

impl Header {
    /// The kit's string-freeing function (`<prefix>_free_string`), if
    /// the header declares one. Generated wrappers free caller-owned
    /// strings through exactly this name — never an assumed one.
    pub fn free_string_fn(&self) -> Option<&str> {
        self.functions
            .iter()
            .map(|f| f.name.as_str())
            .find(|n| n.ends_with("_free_string"))
    }

    /// Every opaque handle type named by any prototype, in
    /// first-appearance order.
    pub fn handle_types(&self) -> Vec<&str> {
        let mut out: Vec<&str> = Vec::new();
        for f in &self.functions {
            let tys = std::iter::once(&f.ret).chain(f.params.iter().map(|p| &p.ty));
            for ty in tys {
                if let Some(n) = ty.handle_name() {
                    if !out.contains(&n) {
                        out.push(n);
                    }
                }
            }
        }
        out
    }
}

/// Names the parser must resolve while classifying: the callback
/// typedefs and concrete structs collected from the same header.
#[derive(Default)]
struct Registry {
    callback_names: Vec<String>,
    struct_names: Vec<String>,
}

impl Registry {
    fn is_callback(&self, name: &str) -> bool {
        self.callback_names.iter().any(|n| n == name)
    }
    fn is_struct(&self, name: &str) -> bool {
        self.struct_names.iter().any(|n| n == name)
    }
}

/// Parse a header's text into its prototypes, callback typedefs and
/// concrete structs.
///
/// # Errors
/// Returns a message naming the offending token for any type outside
/// the pinned grammar, for a prototype that does not parse, or for a
/// duplicate prototype name.
pub fn parse_header(text: &str) -> Result<Header, String> {
    let no_comments = strip_comments(text);
    let no_preproc = strip_preprocessor_lines(&no_comments);
    let statements = split_statements(&no_preproc);

    // Pass 1: function-pointer typedefs, so their names resolve when
    // prototypes and struct fields are classified.
    let mut registry = Registry::default();
    let mut pending_callbacks: Vec<&str> = Vec::new();
    let mut rest: Vec<&str> = Vec::new();
    for stmt in &statements {
        let s = stmt.trim();
        if s.starts_with("typedef") && s.contains("(*") {
            pending_callbacks.push(s);
            if let Some(name) = fn_typedef_name(s) {
                registry.callback_names.push(name);
            }
        } else {
            rest.push(stmt);
        }
    }
    let mut callbacks = Vec::new();
    for s in pending_callbacks {
        callbacks.push(parse_fn_typedef(s, &registry)?);
    }

    // Pass 2: concrete structs (`typedef struct Name { ... } Name`).
    let mut structs: Vec<StructDef> = Vec::new();
    let mut proto_stmts: Vec<&str> = Vec::new();
    for stmt in &rest {
        let s = stmt.trim();
        if s.starts_with("typedef struct") && s.contains('{') {
            let def = parse_struct(s, &registry)?;
            registry.struct_names.push(def.name.clone());
            structs.push(def);
        } else {
            proto_stmts.push(stmt);
        }
    }

    // Pass 3: prototypes.
    let mut functions = Vec::new();
    for stmt in proto_stmts {
        if let Some(f) = parse_statement(stmt, &registry)? {
            if functions.iter().any(|g: &Function| g.name == f.name) {
                return Err(format!("duplicate prototype for '{}'", f.name));
            }
            functions.push(f);
        }
    }
    Ok(Header {
        functions,
        callbacks,
        structs,
    })
}

/// Remove `/* ... */` and `// ...` comments. String literals are not
/// tracked: the collection's headers contain no comment markers inside
/// string literals (the only literal is `"C"` in `extern "C"`).
fn strip_comments(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut out = String::with_capacity(text.len());
    let mut i = 0;
    while i < bytes.len() {
        if i + 1 < bytes.len() && bytes[i] == b'/' && bytes[i + 1] == b'*' {
            // Block comment: replace with a space so tokens on either
            // side never fuse.
            out.push(' ');
            i += 2;
            while i + 1 < bytes.len() && !(bytes[i] == b'*' && bytes[i + 1] == b'/') {
                i += 1;
            }
            i = (i + 2).min(bytes.len());
        } else if i + 1 < bytes.len() && bytes[i] == b'/' && bytes[i + 1] == b'/' {
            out.push(' ');
            while i < bytes.len() && bytes[i] != b'\n' {
                i += 1;
            }
        } else {
            // Push the whole char (headers are ASCII in practice, but
            // never split a UTF-8 sequence).
            let ch_len = utf8_len(bytes[i]);
            out.push_str(&text[i..(i + ch_len).min(text.len())]);
            i += ch_len;
        }
    }
    out
}

fn utf8_len(first: u8) -> usize {
    if first < 0x80 {
        1
    } else if first >> 5 == 0b110 {
        2
    } else if first >> 4 == 0b1110 {
        3
    } else {
        4
    }
}

/// Drop lines whose first non-whitespace character is `#`
/// (`#include`, `#define`, the include guards, `#ifdef` blocks).
fn strip_preprocessor_lines(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for line in text.lines() {
        if line.trim_start().starts_with('#') {
            continue;
        }
        out.push_str(line);
        out.push('\n');
    }
    out
}

/// Split into statements at semicolons that sit at brace depth 0, so
/// a struct or enum body (whose fields end in `;` too) stays in one
/// statement. The semicolons themselves are dropped. The
/// `extern "C" { ... }` wrapper is transparent: its braces do not
/// count toward the depth, so the prototypes inside split normally.
fn split_statements(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut depth = 0i32;
    let mut extern_open = false;
    for ch in text.chars() {
        match ch {
            '{' => {
                if cur.trim_end().ends_with("extern \"C\"") {
                    extern_open = true;
                } else {
                    depth += 1;
                }
                cur.push(ch);
            }
            '}' => {
                if depth == 0 && extern_open {
                    extern_open = false;
                } else {
                    depth -= 1;
                }
                cur.push(ch);
            }
            ';' if depth == 0 => {
                out.push(std::mem::take(&mut cur));
            }
            _ => cur.push(ch),
        }
    }
    if !cur.trim().is_empty() {
        out.push(cur);
    }
    out
}

/// A struct-field declarator name: `abbr` or `abbr[16]` for a
/// fixed-size array field. Returns the name and the array length.
fn parse_declarator_name(tok: &str) -> Option<(String, Option<usize>)> {
    if let Some(open) = tok.find('[') {
        if !tok.ends_with(']') {
            return None;
        }
        let name = &tok[..open];
        let len: usize = tok[open + 1..tok.len() - 1].parse().ok()?;
        if is_identifier(name) && len > 0 {
            return Some((name.to_string(), Some(len)));
        }
        return None;
    }
    if is_identifier(tok) {
        Some((tok.to_string(), None))
    } else {
        None
    }
}

/// The name inside a function-pointer typedef's `(*Name)`.
fn fn_typedef_name(stmt: &str) -> Option<String> {
    let start = stmt.find("(*")? + 2;
    let end = stmt[start..].find(')')? + start;
    let name = stmt[start..end].trim().to_string();
    if is_identifier(&name) {
        Some(name)
    } else {
        None
    }
}

/// Parse `typedef RET (*Name)(params)` (the trailing `;` is already
/// removed by the statement splitter).
fn parse_fn_typedef(stmt: &str, registry: &Registry) -> Result<CallbackDef, String> {
    let s = stmt.trim();
    let Some(name) = fn_typedef_name(s) else {
        return Err(format!(
            "cannot parse function-pointer typedef: '{}'",
            one_line(s)
        ));
    };
    let star = s.find("(*").unwrap();
    let ret_tokens = drop_export_macros(tokenize(&s["typedef".len()..star]));
    let ret =
        classify(&ret_tokens, registry).map_err(|tok| unknown_type(&tok, &name, "return type"))?;
    // The parameter list is the parenthesised text after `(*Name)`.
    let after_name = star + 2 + name.len();
    let Some(open) = s[after_name..].find('(').map(|i| i + after_name) else {
        return Err(format!(
            "cannot parse function-pointer typedef: '{}'",
            one_line(s)
        ));
    };
    if !s.ends_with(')') {
        return Err(format!(
            "cannot parse function-pointer typedef: '{}'",
            one_line(s)
        ));
    }
    let params = parse_params(&s[open + 1..s.len() - 1], registry, &name, true)?;
    Ok(CallbackDef { name, ret, params })
}

/// Parse `typedef struct Name { TYPE field; ... } Name` (the
/// trailing `;` is already removed by the statement splitter).
fn parse_struct(stmt: &str, registry: &Registry) -> Result<StructDef, String> {
    let s = stmt.trim();
    let (Some(open), Some(close)) = (s.find('{'), s.rfind('}')) else {
        return Err(format!("cannot parse struct typedef: '{}'", one_line(s)));
    };
    // The struct's name is the token after the closing brace; fall
    // back to the token after `struct` for the anonymous form.
    let tail = tokenize(&s[close + 1..]);
    let head = tokenize(&s[..open]);
    let name = tail
        .first()
        .cloned()
        .or_else(|| head.get(2).cloned())
        .unwrap_or_default();
    if !is_identifier(&name) {
        return Err(format!("cannot parse struct typedef: '{}'", one_line(s)));
    }
    let mut fields = Vec::new();
    for field in s[open + 1..close].split(';') {
        let field = field.trim();
        if field.is_empty() {
            continue;
        }
        // One declaration may name several fields (`int year, month,
        // day;`): the first carries the type, the rest inherit it.
        let mut inherited: Option<CType> = None;
        for (i, declarator) in field.split(',').enumerate() {
            let declarator = declarator.trim();
            let tokens = tokenize(declarator);
            let Some((raw_name, type_tokens)) = tokens.split_last() else {
                continue;
            };
            let Some((fname, array_len)) = parse_declarator_name(raw_name) else {
                return Err(format!(
                    "cannot parse field '{}' in struct '{}'",
                    one_line(field),
                    name
                ));
            };
            let base = if i == 0 {
                if type_tokens.is_empty() {
                    return Err(format!(
                        "cannot parse field '{}' in struct '{}'",
                        one_line(field),
                        name
                    ));
                }
                // A `char` array element is the collection's byte
                // array; classify would reject a bare `char`.
                let base = if array_len.is_some()
                    && type_tokens.len() == 1
                    && type_tokens[0] == "char"
                {
                    CType::U8
                } else {
                    classify(type_tokens, registry).map_err(|tok| {
                        format!(
                            "unknown type token '{}' in field '{}' of struct '{}': BridgeKit never guesses a mapping",
                            tok, fname, name
                        )
                    })?
                };
                inherited = Some(base.clone());
                base
            } else {
                match &inherited {
                    Some(t) => t.clone(),
                    None => {
                        return Err(format!(
                            "cannot parse field '{}' in struct '{}'",
                            one_line(field),
                            name
                        ))
                    }
                }
            };
            let ty = match array_len {
                Some(n) => CType::Array(Box::new(base), n),
                None => base,
            };
            fields.push(Param { name: fname, ty });
        }
    }
    Ok(StructDef { name, fields })
}

/// Parse one statement. Returns `None` for statements that are not
/// prototypes (typedefs, enums, structs, the braces of the
/// `extern "C"` wrapper, stray fragments).
fn parse_statement(stmt: &str, registry: &Registry) -> Result<Option<Function>, String> {
    let mut s = stmt.trim();
    if s.is_empty() {
        return Ok(None);
    }
    // Unwrap a leading `extern "C" {` (or an enum/struct opener): if
    // the text before the first '{' holds no '(', it is a wrapper or a
    // definition opener, not part of a prototype — cut through it.
    if let Some(brace) = s.find('{') {
        let head = &s[..brace];
        if !head.contains('(') {
            s = s[brace + 1..].trim();
        }
    }
    if s.contains('{') || s.contains('}') {
        return Ok(None); // enum/struct body or the extern closing brace
    }
    if s.starts_with("typedef") {
        return Ok(None);
    }
    let Some(open) = s.find('(') else {
        return Ok(None); // not a prototype (macro remnant, stray text)
    };
    if !s.ends_with(')') {
        return Err(format!("cannot parse declaration: '{}'", one_line(s)));
    }
    let close = s.len() - 1; // the final ')'
    let head_tokens = tokenize(&s[..open]);
    let head_tokens = drop_export_macros(head_tokens);
    let Some((name, ret_tokens)) = head_tokens.split_last() else {
        return Err(format!("cannot parse declaration: '{}'", one_line(s)));
    };
    if !is_identifier(name) {
        return Err(format!(
            "cannot parse declaration: '{}' has no function name",
            one_line(s)
        ));
    }
    let ret =
        classify(ret_tokens, registry).map_err(|tok| unknown_type(&tok, name, "return type"))?;
    let params = parse_params(&s[open + 1..close], registry, name, false)?;
    Ok(Some(Function {
        name: name.clone(),
        ret,
        params,
    }))
}

/// Parse a comma-separated parameter list. With `allow_unnamed`
/// (function-pointer typedefs), a parameter that is only a type gets
/// an empty name; generators synthesize positional names.
fn parse_params(
    params_text: &str,
    registry: &Registry,
    fn_name: &str,
    allow_unnamed: bool,
) -> Result<Vec<Param>, String> {
    let params_text = params_text.trim();
    let mut params = Vec::new();
    if params_text.is_empty() || params_text == "void" {
        return Ok(params);
    }
    for part in params_text.split(',') {
        let part = part.trim();
        if part.contains('(') || part.contains(')') {
            return Err(format!(
                "unsupported parameter '{}' in prototype '{}': nested declarators are outside the header grammar",
                one_line(part),
                fn_name
            ));
        }
        let tokens = drop_export_macros(tokenize(part));
        if tokens.is_empty() {
            return Err(format!("empty parameter in prototype '{}'", fn_name));
        }
        // Named form first: the last token is the name, the rest the
        // type. If that does not classify and unnamed parameters are
        // allowed, the whole token list may be the type itself.
        let named = if tokens.len() >= 2 {
            let (pname, ptokens) = tokens.split_last().unwrap();
            if is_identifier(pname) {
                match classify(ptokens, registry) {
                    Ok(ty) => Some(Param {
                        name: pname.clone(),
                        ty,
                    }),
                    Err(_) => None,
                }
            } else {
                None
            }
        } else {
            None
        };
        match named {
            Some(p) => params.push(p),
            None if allow_unnamed => {
                let ty = classify(&tokens, registry).map_err(|tok| {
                    unknown_type(&tok, fn_name, &format!("parameter '{}'", one_line(part)))
                })?;
                params.push(Param {
                    name: String::new(),
                    ty,
                });
            }
            None => {
                // Re-run the named classification to surface its error
                // (or the missing-name error) in the house wording.
                let (pname, ptokens) = tokens.split_last().unwrap();
                if !is_identifier(pname) {
                    return Err(format!(
                        "parameter '{}' in prototype '{}' has no name",
                        one_line(part),
                        fn_name
                    ));
                }
                if ptokens.is_empty() {
                    return Err(format!(
                        "parameter '{}' in prototype '{}' has no type",
                        pname, fn_name
                    ));
                }
                let ty = classify(ptokens, registry).map_err(|tok| {
                    unknown_type(&tok, fn_name, &format!("parameter '{}'", pname))
                })?;
                params.push(Param {
                    name: pname.clone(),
                    ty,
                });
            }
        }
    }
    Ok(params)
}

/// Split a declaration fragment into tokens: identifiers/numbers stay
/// whole, `*` is always its own token.
fn tokenize(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    for ch in text.chars() {
        if ch == '*' {
            if !cur.is_empty() {
                out.push(std::mem::take(&mut cur));
            }
            out.push("*".to_string());
        } else if ch.is_whitespace() {
            if !cur.is_empty() {
                out.push(std::mem::take(&mut cur));
            }
        } else {
            cur.push(ch);
        }
    }
    if !cur.is_empty() {
        out.push(cur);
    }
    out
}

/// Export macros are all-caps tokens ending in `_API`
/// (`NO_API`, `WA_API`, `SG_API`). They carry no type information.
fn drop_export_macros(tokens: Vec<String>) -> Vec<String> {
    tokens
        .into_iter()
        .filter(|t| {
            !(t.len() > 4
                && t.ends_with("_API")
                && t.chars()
                    .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_'))
        })
        .collect()
}

fn is_identifier(tok: &str) -> bool {
    let mut chars = tok.chars();
    match chars.next() {
        Some(c) if c.is_ascii_alphabetic() || c == '_' => {
            chars.all(|c| c.is_ascii_alphanumeric() || c == '_')
        }
        _ => false,
    }
}

/// The scalar (non-pointer) types, by token list. Shared by the
/// plain, pointer and const-pointer classification arms.
fn scalar_of(toks: &[&str]) -> Option<CType> {
    let ty = match toks {
        ["int"] => CType::Int,
        ["unsigned", "int"] => CType::UInt,
        ["uint32_t"] => CType::U32,
        ["uint64_t"] => CType::U64,
        ["int64_t"] => CType::I64,
        ["uint8_t"] => CType::U8,
        ["size_t"] => CType::SizeT,
        ["float"] => CType::F32,
        ["double"] => CType::F64,
        _ => return None,
    };
    Some(ty)
}

/// Map a token list to a grammar type. On failure returns the first
/// token that is not part of any known type, so the error can name it.
fn classify(tokens: &[String], registry: &Registry) -> Result<CType, String> {
    let toks: Vec<&str> = tokens.iter().map(String::as_str).collect();
    if let Some(scalar) = scalar_of(&toks) {
        return Ok(scalar);
    }
    let ty = match toks.as_slice() {
        ["void"] => CType::Void,
        ["const", "char", "*"] => CType::ConstCharPtr,
        ["char", "*"] => CType::CharPtr,
        ["char", "*", "*"] => CType::CharPtrPtr,
        ["void", "*"] => CType::VoidPtr,
        ["const", "void", "*"] => CType::ConstVoidPtr,
        [name, "*", "*"] if is_handle_name(name) => CType::HandlePtrPtr((*name).to_string()),
        ["const", name, "*"] if registry.is_struct(name) => {
            CType::ConstStructPtr((*name).to_string())
        }
        [name, "*"] if registry.is_struct(name) => CType::StructPtr((*name).to_string()),
        ["const", name, "*"] if is_handle_name(name) => CType::ConstHandlePtr((*name).to_string()),
        [name, "*"] if is_handle_name(name) => CType::HandlePtr((*name).to_string()),
        [name] if registry.is_callback(name) => CType::Callback((*name).to_string()),
        _ => {
            // Scalar pointer forms: `T *`, `T **` and `const T *`
            // for the numeric scalars.
            if toks.last() == Some(&"*") {
                if toks.first() == Some(&"const") {
                    if let Some(scalar) = scalar_of(&toks[1..toks.len() - 1]) {
                        return Ok(CType::ConstScalarPtr(Box::new(scalar)));
                    }
                } else if toks.len() >= 3 && toks[toks.len() - 2] == "*" {
                    if let Some(scalar) = scalar_of(&toks[..toks.len() - 2]) {
                        return Ok(CType::ScalarPtrPtr(Box::new(scalar)));
                    }
                } else if let Some(scalar) = scalar_of(&toks[..toks.len() - 1]) {
                    return Ok(CType::ScalarPtr(Box::new(scalar)));
                }
            }
            const KNOWN: [&str; 13] = [
                "const", "char", "void", "int", "unsigned", "uint32_t", "uint64_t", "int64_t",
                "uint8_t", "size_t", "float", "double", "*",
            ];
            let bad = toks
                .iter()
                .find(|t| !KNOWN.contains(t) && !is_handle_name(t))
                .copied()
                .unwrap_or_else(|| toks.first().copied().unwrap_or(""));
            return Err(bad.to_string());
        }
    };
    Ok(ty)
}

/// Opaque handles are capitalized typedef'd struct names
/// (`NoCenter`, `WaWatcher`). Requiring the capital keeps a lowercase
/// unknown type like `wchar_t *` an error instead of a "handle".
fn is_handle_name(tok: &str) -> bool {
    is_identifier(tok) && tok.chars().next().is_some_and(|c| c.is_ascii_uppercase())
}

fn unknown_type(token: &str, fn_name: &str, what: &str) -> String {
    format!(
        "unknown type token '{}' in {} of prototype '{}': BridgeKit never guesses a mapping — extend the header grammar in src/header.rs if this type is real",
        token, what, fn_name
    )
}

fn one_line(s: &str) -> String {
    s.split_whitespace().collect::<Vec<_>>().join(" ")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_the_core_shapes() {
        let h = parse_header(
            "XX_API const char *xx_version(void);\n\
             XX_API int xx_do(Thing *t, const char *json, char **out, uint64_t n, unsigned int flags);\n\
             XX_API void xx_free_string(char *p);\n",
        )
        .unwrap();
        assert_eq!(h.functions.len(), 3);
        assert_eq!(h.functions[0].ret, CType::ConstCharPtr);
        assert_eq!(h.functions[1].params.len(), 5);
        assert_eq!(h.functions[1].params[1].ty, CType::ConstCharPtr);
        assert_eq!(h.functions[1].params[2].ty, CType::CharPtrPtr);
        assert_eq!(h.functions[1].params[3].ty, CType::U64);
        assert_eq!(h.functions[1].params[4].ty, CType::UInt);
        assert_eq!(h.free_string_fn(), Some("xx_free_string"));
        assert_eq!(h.handle_types(), vec!["Thing"]);
    }

    #[test]
    fn skips_typedefs_enums_and_extern_wrappers() {
        let h = parse_header(
            "#ifndef X_H\n#define X_H\n\
             typedef struct Thing Thing;\n\
             enum { XX_OK = 0, XX_ERR = 1 };\n\
             extern \"C\" {\n\
             XX_API int xx_count(Thing *t);\n\
             }\n#endif\n",
        )
        .unwrap();
        assert_eq!(h.functions.len(), 1);
        assert_eq!(h.functions[0].name, "xx_count");
    }

    #[test]
    fn unknown_type_names_the_token() {
        let err = parse_header("XX_API int xx_bad(wchar_t factor);").unwrap_err();
        assert!(err.contains("'wchar_t'"), "error was: {err}");
        let err = parse_header("XX_API long double xx_len(void);").unwrap_err();
        assert!(err.contains("'long'"), "error was: {err}");
    }

    #[test]
    fn multiline_prototype_parses() {
        let h = parse_header("XX_API int xx_long(Thing *t,\n               const char *json,\n               char **out);\n").unwrap();
        assert_eq!(h.functions[0].params.len(), 3);
    }

    #[test]
    fn parses_the_2026_survey_types() {
        let h = parse_header(
            "XX_API int xx_schema(Thing *t, int64_t *out);\n\
             XX_API void xx_free_buffer(uint8_t *p, size_t len);\n\
             XX_API uint64_t xx_load(const uint8_t *data, size_t len);\n\
             XX_API int xx_encode(Thing *t, uint8_t **out_ptr, size_t *out_len);\n\
             XX_API int xx_add_page(uint64_t h, double width, const float *query);\n",
        )
        .unwrap();
        assert_eq!(
            h.functions[0].params[1].ty,
            CType::ScalarPtr(Box::new(CType::I64))
        );
        assert!(h.functions[0].params[1].is_out_param());
        assert_eq!(
            h.functions[1].params[0].ty,
            CType::ScalarPtr(Box::new(CType::U8))
        );
        assert!(!h.functions[1].params[0].is_out_param());
        assert_eq!(
            h.functions[2].params[0].ty,
            CType::ConstScalarPtr(Box::new(CType::U8))
        );
        assert_eq!(
            h.functions[3].params[1].ty,
            CType::ScalarPtrPtr(Box::new(CType::U8))
        );
        assert_eq!(h.functions[4].params[1].ty, CType::F64);
        assert_eq!(
            h.functions[4].params[2].ty,
            CType::ConstScalarPtr(Box::new(CType::F32))
        );
    }

    #[test]
    fn parses_callbacks_and_structs() {
        let h = parse_header(
            "typedef int (*XxListFn)(void *user_data, const char *uri, char **out_json);\n\
             typedef struct XxCallbacks {\n\
                 uint32_t struct_size;\n\
                 XxListFn list;\n\
             } XxCallbacks;\n\
             XX_API int xx_register(const XxCallbacks *callbacks, void *user_data);\n\
             XX_API int xx_run(const char *spec, XxListFn cb);\n",
        )
        .unwrap();
        assert_eq!(h.callbacks.len(), 1);
        assert_eq!(h.callbacks[0].name, "XxListFn");
        assert_eq!(h.callbacks[0].params.len(), 3);
        assert_eq!(h.structs.len(), 1);
        assert_eq!(h.structs[0].name, "XxCallbacks");
        assert_eq!(h.structs[0].fields.len(), 2);
        assert_eq!(
            h.structs[0].fields[1].ty,
            CType::Callback("XxListFn".to_string())
        );
        assert_eq!(
            h.functions[0].params[0].ty,
            CType::ConstStructPtr("XxCallbacks".to_string())
        );
        assert_eq!(
            h.functions[1].params[1].ty,
            CType::Callback("XxListFn".to_string())
        );
    }
}
