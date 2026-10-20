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
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKEL = os.path.join(KIT, "templates", "dll-skeleton")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="display/repo name, e.g. FastSearch")
    ap.add_argument("--prefix", required=True, help="FFI prefix, e.g. fs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--description", default="TODO: one-line description")
    a = ap.parse_args()

    crate = a.name.replace("_", "-").lower()
    # kebab-case from CamelCase
    kebab = []
    for i, ch in enumerate(a.name):
        if ch.isupper() and i > 0:
            kebab.append("-")
        kebab.append(ch.lower())
    crate = "".join(kebab)
    tokens = {
        "{{REPO}}": a.name,
        "{{CRATE}}": crate,
        "{{CRATE_UNDERSCORE}}": crate.replace("-", "_"),
        "{{HEADER}}": crate.replace("-", "") + ".h",
        "{{GUARD}}": a.name.upper() + "_H",
        "{{PREFIX}}": a.prefix,
        "{{PREFIX_UPPER}}": a.prefix.upper(),
        "{{DESCRIPTION}}": a.description,
    }
    if os.path.exists(a.out):
        sys.exit(f"refusing to overwrite existing {a.out}")
    for root, _dirs, files in os.walk(SKEL):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, SKEL)
            if f == "skeleton.h":
                rel = os.path.join(os.path.dirname(rel), tokens["{{HEADER}}"])
            dst = os.path.join(a.out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            text = open(src, encoding="utf-8").read()
            for k, v in tokens.items():
                text = text.replace(k, v)
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("wrote", dst)
    # Standard repo files
    shutil.copy(os.path.join(KIT, "templates", "ci.yml"), os.path.join(a.out, "ci.yml"))
    with open(os.path.join(a.out, ".gitignore"), "w") as fh:
        fh.write("/target\n")
    print(f"Done. Next: cd {a.out} && cargo test && ../windevkit/tools/gate.sh")


if __name__ == "__main__":
    main()
