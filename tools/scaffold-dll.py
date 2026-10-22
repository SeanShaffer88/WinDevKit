#!/usr/bin/env python3
"""Scaffold a new DLL project from templates/dll-skeleton.

Usage:
  scaffold-dll.py --name FastSearch --prefix fs --out ~/workspace/fastsearch \
                  --description "Instant NTFS file search behind one C call"

Tokens replaced across the skeleton: {{REPO}} (display name), {{CRATE}}
(kebab-case crate), {{CRATE_UNDERSCORE}}, {{HEADER}}, {{GUARD}},
{{PREFIX}}, {{PREFIX_UPPER}}, {{DESCRIPTION}}.
The header skeleton.h is renamed to the crate's header name.
"""
import argparse
import os
import shutil
import re
import json
import hashlib
from pathlib import Path
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKEL = os.path.join(KIT, "templates", "dll-skeleton")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="display/repo name, e.g. FastSearch")
    ap.add_argument("--prefix", required=True, help="FFI prefix, e.g. fs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--description", default="TODO: one-line description")
    ap.add_argument("--with-win-common", type=Path,
                    help="vendor a local reviewed WinCommon checkout; adds an offline path dependency")
    a = ap.parse_args()
    common_files = []
    if a.with_win_common:
        common_root = a.with_win_common.resolve()
        common_files = [common_root / "Cargo.toml", common_root / "LICENSE", common_root / "README.md"] + sorted((common_root / "src").rglob("*.rs"))
        if not (common_root / "src/lib.rs").is_file() or not all(p.is_file() and not p.is_symlink() for p in common_files):
            ap.error("WinCommon must contain regular Cargo.toml, LICENSE, README.md and src/*.rs files")
        import tomllib
        manifest = tomllib.loads((common_root / "Cargo.toml").read_text(encoding="utf-8"))
        if manifest.get("package", {}).get("name") != "win-common" or manifest.get("dependencies"):
            ap.error("expected the std-only win-common crate")

    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*", a.name):
        ap.error("name must be an ASCII identifier, optionally separated by - or _")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.prefix):
        ap.error("prefix must start with a lowercase ASCII letter and contain only a-z, digits, _")
    if any(ord(c) < 32 or ord(c) == 127 for c in a.description):
        ap.error("description must be a single line without control characters")
    crate = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", a.name)
    crate = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", crate).replace("_", "-").lower()
    tokens = {
        "{{REPO}}": a.name,
        "{{CRATE}}": crate,
        "{{CRATE_UNDERSCORE}}": crate.replace("-", "_"),
        "{{HEADER}}": crate.replace("-", "") + ".h",
        "{{GUARD}}": crate.replace("-", "_").upper() + "_H",
        "{{PREFIX}}": a.prefix,
        "{{PREFIX_UPPER}}": a.prefix.upper(),
        "{{DESCRIPTION}}": json.dumps(a.description, ensure_ascii=False)[1:-1],
    }
    if os.path.lexists(a.out):
        sys.exit(f"refusing to overwrite existing {a.out}")
    os.makedirs(a.out, exist_ok=False)  # reserve output before writing files
    for root, _dirs, files in os.walk(SKEL):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, SKEL)
            if f == "skeleton.h":
                rel = os.path.join(os.path.dirname(rel), tokens["{{HEADER}}"])
            dst = os.path.join(a.out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, encoding="utf-8") as source:
                text = source.read()
            for k, v in tokens.items():
                text = text.replace(k, v)
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("wrote", dst)
    if a.with_win_common:
        inventory = {}
        for source in common_files:
            rel = source.relative_to(common_root)
            dest = Path(a.out) / "vendor/win-common" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            dest.write_bytes(data)
            inventory[rel.as_posix()] = hashlib.sha256(data).hexdigest()
        (Path(a.out) / "vendor/win-common/VENDORED.json").write_text(
            json.dumps({"source": "https://github.com/SeanShaffer88/WinCommon", "files_sha256": inventory}, indent=2) + "\n", encoding="utf-8")
        manifest_path = Path(a.out) / "Cargo.toml"
        text = manifest_path.read_text(encoding="utf-8").replace(
            "[dependencies]", '[dependencies]\n# Shared, audited std-only helpers; vendored for offline reproducibility.\nwin-common = { path = "vendor/win-common" }')
        manifest_path.write_text(text, encoding="utf-8")
        lib_path = Path(a.out) / "src/lib.rs"
        text = lib_path.read_text(encoding="utf-8")
        start = text.index("/// Escape a string")
        end = text.index("#[cfg(test)]", start)
        text = text[:start] + "pub use win_common::json::escape as json_escape;\n\n" + text[end:]
        lib_path.write_text(text, encoding="utf-8")
        # Retain the template's public names and header; use the shared TLS
        # and ownership implementation rather than copying its private state.
        ffi = """//! C exports backed by the vendored win-common crate.
use std::os::raw::{c_char, c_int};
pub use win_common::ffi::set_error;

pub fn guard<T>(f: impl FnOnce() -> T) -> Result<T, i32> {
    win_common::ffi::guard_value(f).map_err(|_| {
        set_error(crate::ERR_INTERNAL, "internal panic caught at FFI boundary");
        crate::ERR_INTERNAL
    })
}
#[no_mangle]
pub extern "C" fn PREFIX_version() -> *const c_char { c"0.1.0".as_ptr() }
#[no_mangle]
pub extern "C" fn PREFIX_last_error() -> *const c_char { win_common::ffi::last_error_ptr() }
#[no_mangle]
pub extern "C" fn PREFIX_last_error_code() -> c_int { win_common::ffi::last_error_code() }
#[allow(clippy::not_unsafe_ptr_arg_deref)]
#[no_mangle]
pub extern "C" fn PREFIX_free_string(p: *mut c_char) {
    // SAFETY: C ABI contract requires null or an unfreed result from this DLL.
    unsafe { win_common::ffi::free_c_string(p) }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn shared_guard_contains_panics() {
        assert_eq!(guard(|| panic!("fixture")), Err(crate::ERR_INTERNAL));
        assert_eq!(PREFIX_last_error_code(), crate::ERR_INTERNAL);
    }
}
""".replace("PREFIX", a.prefix)
        (Path(a.out) / "src/ffi.rs").write_text(ffi, encoding="utf-8")
    # Standard repo files
    shutil.copy(os.path.join(KIT, "templates", "ci.yml"), os.path.join(a.out, "ci.yml"))
    with open(os.path.join(a.out, ".gitignore"), "w") as fh:
        fh.write("/target\n")
    print(f"Done. Next: cd {a.out} && cargo generate-lockfile && cargo fmt --all && cargo test && ../windevkit/tools/gate.sh")


if __name__ == "__main__":
    main()
