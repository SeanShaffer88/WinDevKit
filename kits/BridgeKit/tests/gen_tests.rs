//! Generation tests: golden outputs for both generators over the
//! three real-kit fixtures, plus the grammar's failure modes.

use bridgekit::header::parse_header;
use std::path::PathBuf;

fn fixture(name: &str) -> String {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(name);
    std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("read {:?}: {}", path, e))
}

fn golden(name: &str) -> String {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/golden")
        .join(name);
    let text = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("read {:?}: {}", path, e));
    text.replace("\r\n", "\n")
}

#[test]
fn golden_cs_notifykit() {
    let header = parse_header(&fixture("notifykit.h")).unwrap();
    let out = bridgekit::gen_cs::generate(&header, "notifykit.h", "notify_kit.dll").unwrap();
    assert_eq!(out, golden("notifykit.cs"));
}

#[test]
fn golden_cs_signkit() {
    let header = parse_header(&fixture("signkit.h")).unwrap();
    let out = bridgekit::gen_cs::generate(&header, "signkit.h", "sign_kit.dll").unwrap();
    assert_eq!(out, golden("signkit.cs"));
}

#[test]
fn golden_rs_watchkit() {
    let header = parse_header(&fixture("watchkit.h")).unwrap();
    let out = bridgekit::gen_rs::generate(&header, "watchkit.h").unwrap();
    assert_eq!(out, golden("watchkit.rs"));
}

#[test]
fn golden_rs_notifykit() {
    let header = parse_header(&fixture("notifykit.h")).unwrap();
    let out = bridgekit::gen_rs::generate(&header, "notifykit.h").unwrap();
    assert_eq!(out, golden("notifykit.rs"));
}

#[test]
fn fixtures_parse_to_the_expected_shapes() {
    let no = parse_header(&fixture("notifykit.h")).unwrap();
    assert_eq!(no.functions.len(), 10);
    assert_eq!(no.handle_types(), vec!["NoCenter", "NoTray"]);
    assert_eq!(no.free_string_fn(), Some("no_free_string"));

    let wa = parse_header(&fixture("watchkit.h")).unwrap();
    assert_eq!(wa.functions.len(), 8);
    assert_eq!(wa.handle_types(), vec!["WaWatcher"]);

    let sg = parse_header(&fixture("signkit.h")).unwrap();
    assert_eq!(sg.functions.len(), 7);
    assert!(sg.handle_types().is_empty());
}

#[test]
fn cs_class_is_always_public() {
    // The historical failure: non-public [DllImport] members compile
    // and then fail at call time. Pin the generated shape.
    let header = parse_header(&fixture("signkit.h")).unwrap();
    let out = bridgekit::gen_cs::generate(&header, "signkit.h", "sign_kit.dll").unwrap();
    assert!(out.contains("public static partial class SignKit"));
    assert!(out.contains("public static extern"));
    assert!(!out.contains("internal static"));
}

#[test]
fn golden_cs_scalars() {
    let header = parse_header(&fixture("scalars.h")).unwrap();
    let out = bridgekit::gen_cs::generate(&header, "scalars.h", "scalars_kit.dll").unwrap();
    assert_eq!(out, golden("scalars.cs"));
}

#[test]
fn golden_rs_scalars() {
    let header = parse_header(&fixture("scalars.h")).unwrap();
    let out = bridgekit::gen_rs::generate(&header, "scalars.h").unwrap();
    assert_eq!(out, golden("scalars.rs"));
}

#[test]
fn scalars_fixture_parses_to_the_expected_shape() {
    let h = parse_header(&fixture("scalars.h")).unwrap();
    assert_eq!(h.functions.len(), 9);
    assert_eq!(h.callbacks.len(), 2);
    assert_eq!(h.structs.len(), 1);
    assert_eq!(h.structs[0].fields.len(), 3);
}

#[test]
fn every_shipped_kit_header_parses_and_generates() {
    // In the monorepo, every sibling kit's shipped header must parse
    // and generate in both languages - that is the collection-wide
    // claim the README makes. Standalone checkouts skip this test.
    let kits_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("..");
    if !kits_dir.join("SettingsKit").is_dir() {
        return;
    }
    let mut checked = 0;
    for entry in std::fs::read_dir(&kits_dir).unwrap() {
        let dir = entry.unwrap().path();
        let include = dir.join("include");
        if !include.is_dir() {
            continue;
        }
        for header_path in std::fs::read_dir(&include).unwrap() {
            let header_path = header_path.unwrap().path();
            if header_path.extension().is_none_or(|e| e != "h") {
                continue;
            }
            let text = std::fs::read_to_string(&header_path).unwrap();
            let header = parse_header(&text)
                .unwrap_or_else(|e| panic!("{:?} must parse: {}", header_path, e));
            bridgekit::gen_cs::generate(&header, "kit.h", "kit.dll")
                .unwrap_or_else(|e| panic!("{:?} must generate C#: {}", header_path, e));
            bridgekit::gen_rs::generate(&header, "kit.h")
                .unwrap_or_else(|e| panic!("{:?} must generate Rust: {}", header_path, e));
            checked += 1;
        }
    }
    assert!(
        checked >= 30,
        "expected the whole collection, got {checked}"
    );
}

#[test]
fn unknown_type_is_a_hard_error_naming_the_token() {
    let err = parse_header(&fixture("badtype.h")).unwrap_err();
    assert!(err.contains("'wchar_t'"), "error was: {err}");
    assert!(err.contains("bk_scale"), "error was: {err}");

    let err = parse_header("BK_API intptr_t bk_measure(BkThing *t);").unwrap_err();
    assert!(err.contains("'intptr_t'"), "error was: {err}");

    let err = parse_header("BK_API int bk_set(long double count);").unwrap_err();
    assert!(err.contains("'long'"), "error was: {err}");
}

#[test]
fn owned_string_result_without_free_string_is_an_error() {
    // A char* result with no declared <prefix>_free_string cannot be
    // wrapped safely; both generators must refuse, not improvise.
    let header = parse_header("BK_API char *bk_make(const char *name);").unwrap();
    let err = bridgekit::gen_cs::generate(&header, "badtype.h", "bad_kit.dll").unwrap_err();
    assert!(err.contains("free_string"), "error was: {err}");
    let err = bridgekit::gen_rs::generate(&header, "badtype.h").unwrap_err();
    assert!(err.contains("free_string"), "error was: {err}");
}
