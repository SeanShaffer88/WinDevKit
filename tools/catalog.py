#!/usr/bin/env python3
"""Generate and check docs/CATALOG.md, the Windows DLL Collection catalog.

The catalog is generated from docs/CATALOG_DATA.json (groups, one-line
descriptions, external kits) joined with each kit's own Cargo.toml
version and folder under kits/. Hand-editing CATALOG.md is therefore
pointless: edit the data file and run

    python tools/catalog.py generate

`check` (the default) fails when the data and the tree disagree or the
generated file is stale: a kit under kits/ missing from the data, a
data entry with no kit folder, a version that does not come from
Cargo.toml, or a download URL that does not point at this repository's
own Releases. That is the guard against the failure recorded in
docs/PAIN_POINTS.md #50, where the catalog promised ready downloads
from standalone kit repositories that no longer existed.

`check --online` additionally HEAD-checks every URL in the generated
catalog and reports the dead ones. It needs the network, so CI runs
the offline check and the online one is run by hand (and before any
release batch).

Python 3.10+, standard library only.
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "docs" / "CATALOG_DATA.json"
CATALOG_PATH = ROOT / "docs" / "CATALOG.md"
KITS_DIR = ROOT / "kits"
REPO = "SeanShaffer88/WinDevKit"


def kit_version(kit: str) -> str:
    cargo = KITS_DIR / kit / "Cargo.toml"
    with cargo.open("rb") as fh:
        return tomllib.load(fh)["package"]["version"]


def kit_header(kit: str) -> str | None:
    include = KITS_DIR / kit / "include"
    if include.is_dir():
        headers = sorted(p.name for p in include.glob("*.h"))
        if headers:
            return headers[0]
    return None


def download_url(kit: str, version: str) -> str:
    tag = f"{kit}-v{version}"
    return (
        f"https://github.com/{REPO}/releases/download/{tag}/"
        f"{kit}-{version}-x64.zip"
    )


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def data_kit_names(data: dict) -> list[str]:
    return [
        entry["name"]
        for group in data["groups"]
        for entry in group["kits"]
    ]


def tree_kit_names() -> list[str]:
    return sorted(p.name for p in KITS_DIR.iterdir() if p.is_dir())


def check_data(data: dict) -> list[str]:
    """Offline consistency checks between the data file and the tree."""
    problems: list[str] = []
    named = data_kit_names(data)
    tree = tree_kit_names()
    if len(named) != len(set(named)):
        problems.append("catalog data lists a kit more than once")
    for kit in tree:
        if kit not in named:
            problems.append(f"kit {kit} is under kits/ but missing from catalog data")
    for kit in named:
        if kit not in tree:
            problems.append(f"catalog data lists {kit} but kits/{kit} does not exist")
        else:
            try:
                kit_version(kit)
            except Exception as exc:  # unreadable Cargo.toml
                problems.append(f"kit {kit}: cannot read version from Cargo.toml ({exc})")
    seen_external: set[str] = set()
    for entry in data.get("external", []):
        if entry["name"] in seen_external:
            problems.append(f"external kit {entry['name']} listed twice")
        seen_external.add(entry["name"])
        for field in ("repo", "download"):
            if not entry[field].startswith("https://github.com/"):
                problems.append(
                    f"external kit {entry['name']}: {field} is not a GitHub URL"
                )
        if entry["name"] in named:
            problems.append(
                f"{entry['name']} is both an in-repo kit and an external kit"
            )
    return problems


def render(data: dict) -> str:
    lines: list[str] = []
    total = len(data_kit_names(data))
    lines.append("# The Windows DLL Collection — Catalog")
    lines.append("")
    lines.append("## TL;DR")
    lines.append("")
    lines.append(
        f"{total} small Windows DLLs that each do one common job — watching "
        "folders, making thumbnails, showing notifications, handling settings — "
        "so programs do not have to reinvent them. Every kit is free (MIT) and "
        "ships as a ready-to-use download from this repository's Releases: the "
        "DLL, a C header, and an import library. Any programming language that "
        "can call C functions can use them."
    )
    lines.append("")
    lines.append("## How every kit works")
    lines.append("")
    lines.append("- Plain C interface (a header file is included), so C, C++, C#, Rust, Python,")
    lines.append("  PowerShell and anything else with a C-calling feature can use them.")
    lines.append("- Settings and results travel as JSON text — no structs to line up.")
    lines.append("- Errors come back as readable text, never as a crash.")
    lines.append("- No Rust crate dependencies: each kit builds from its own source in this")
    lines.append("  repository. Two kits use native engines, named in their rows below")
    lines.append("  (OCRKit vendors its OCR engine; EmbedKit loads a user-supplied ONNX Runtime).")
    lines.append("- Built from Rust with the full test suite in the repository; the whole")
    lines.append("  collection is gated by one CI workflow in this repository.")
    lines.append("")
    lines.append(data["intro"]["field_note"])
    lines.append("")
    lines.append("Downloads are x64 and unsigned (there is no code-signing certificate);")
    lines.append("Windows may show a SmartScreen prompt on first use. Every download page")
    lines.append("also carries a `SHA256SUMS.txt` — check your download against it.")
    lines.append("")
    lines.append(
        "This file is generated by `tools/catalog.py` from "
        "`docs/CATALOG_DATA.json` and each kit's `Cargo.toml`. Do not edit "
        "it by hand; run `python tools/catalog.py generate`."
    )
    for group in data["groups"]:
        lines.append("")
        lines.append(f"## {group['title']}")
        lines.append("")
        lines.append("| Kit | What it does | Version | Download |")
        lines.append("|---|---|---|---|")
        for entry in group["kits"]:
            kit = entry["name"]
            version = kit_version(kit)
            blurb = entry["blurb"]
            if entry.get("note"):
                blurb = f"{blurb} _{entry['note']}_"
            lines.append(
                f"| [{kit}](../kits/{kit}/) | {blurb} | v{version} | "
                f"[DLL zip]({download_url(kit, version)}) |"
            )
    lines.append("")
    lines.append("## Hosted in their own repositories")
    lines.append("")
    lines.append(
        "These family members were never merged into this repository; their "
        "own repositories and releases are live (checked 2026-11-12)."
    )
    lines.append("")
    lines.append("| Kit | What it does | Version | Download |")
    lines.append("|---|---|---|---|")
    for entry in data.get("external", []):
        lines.append(
            f"| [{entry['name']}]({entry['repo']}) | {entry['blurb']} | "
            f"v{entry['version']} | [Download]({entry['download']}) |"
        )
    if data.get("unpublished"):
        lines.append("")
        lines.append("## Not currently published")
        lines.append("")
        for entry in data["unpublished"]:
            lines.append(f"- **{entry['name']}** — {entry['blurb']}")
    lines.append("")
    lines.append("## License")
    lines.append("")
    lines.append("Every kit is MIT-licensed and free, including for commercial use.")
    lines.append("")
    return "\n".join(lines)


def check_online(text: str) -> list[str]:
    urls = sorted(set(re.findall(r"\((https://[^)]+)\)", text)))
    dead: list[str] = []
    for url in urls:
        req = urllib.request.Request(url, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception as exc:  # network failure counts as unknown, say so
            dead.append(f"{url} (unreachable: {exc})")
            continue
        if code >= 400:
            dead.append(f"{url} (HTTP {code})")
    return dead


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "check"
    online = "--online" in argv[2:]
    data = load_data()
    problems = check_data(data)
    if mode == "generate":
        if problems:
            for problem in problems:
                print(f"error: {problem}")
            return 1
        CATALOG_PATH.write_text(render(data), encoding="utf-8")
        print(f"wrote {CATALOG_PATH.relative_to(ROOT)}")
        return 0
    if mode == "check":
        expected = render(data) if not problems else ""
        if CATALOG_PATH.exists():
            actual = CATALOG_PATH.read_text(encoding="utf-8")
            if expected and actual != expected:
                problems.append(
                    "docs/CATALOG.md is stale; run `python tools/catalog.py generate`"
                )
        else:
            problems.append("docs/CATALOG.md does not exist")
        if online and not problems:
            problems.extend(check_online(expected))
        for problem in problems:
            print(f"error: {problem}")
        if problems:
            return 1
        print("catalog ok")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
