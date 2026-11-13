# Install and use

## Get the repository

```sh
git clone https://github.com/SeanShaffer88/WinDevKit.git
```

Everything is MIT licensed and free.

## Use a kit

**From source** — each kit is a standalone Rust crate:

```sh
cd WinDevKit/kits/<KitName>
cargo build --release --locked
```

The DLL, its import library (`.dll.lib`) and the C header
(`include/`) are what you consume; every kit's own README
documents its functions.

**Prebuilt** — every kit is released as a ready-to-use x64 zip
(DLL + import lib + header + README + LICENSE) from this
repository's Releases; start from the catalog in
[`CATALOG.md`](CATALOG.md), which links each kit's download.
Every release carries a `SHA256SUMS.txt` — verify your download
against it. (Kits were originally released from standalone
repositories; those are gone, and this repository is now the only
download source.)

## Use the tools

The tools in `tools/` are Python (3.10 or newer) and shell
scripts; run them in place. Start a new DLL in the house style
with:

```sh
python tools/scaffold-dll.py
```

Run the quality gate on any Rust Windows crate with
`tools/gate.sh`, or across all kits with `tools/gate-kits.sh`.

## Use the templates

Copy what you need from `templates/` into your project — the
canonical CI workflow, the release workflow, the DLL skeleton,
app manifests and the checklists each note any setup they need
in their own headers.
