# Roadmap

## Done

- The 34-kit DLL collection, built out from the approved
  expansion and field-verified end to end on a real Windows
  machine (smoke pack 116/116 plus both manual demos,
  2026-10-28).
- Download releases for every kit from this repository (the
  standalone repositories the original releases lived in were
  deleted after the merge; the full collection was re-released
  from here on 2026-11-12, in one `kits-release` ALL dispatch).
- The collection catalog (`docs/CATALOG.md`) — generated from the
  kits' own folders and versions by `tools/catalog.py` and checked
  in CI, so it cannot drift from what actually downloads.
- BridgeKit's grammar covers every shipped kit header (v0.2.0):
  bindings generate for all 33 headers and compile in C# and Rust.
- Runnable examples (`examples/`): SettingsKit from C# (BridgeKit-
  generated binding) and from Python (ctypes).
- FastSearch and HardwareInfo folded into the monorepo
  (2026-11-12): the two family members whose standalone
  repositories were deleted are kits again — the collection
  stands at 36 kits, all released from this repository.
- The monorepo merge (2026-11-01): one repository, one CI gate
  (`kits-ci`, 34/34 green), one release workflow (`kits-release`),
  static-CRT builds for every kit.
- First kit release cut from the monorepo: OCRKit v0.1.1
  (2026-11-01), its assets re-downloaded and hash-verified.
- Field check of a static-CRT build: the OCRKit v0.1.1 DLL
  passed its field test on a real Windows machine (2026-11-01) —
  the download matched its published SHA-256 sum, the DLL loads
  and reports its version, and the OCR engine responds with a
  real engine error when its language data is absent.

## Next

- (Nothing queued — the three items below landed 2026-11-13;
  new roadmap items follow the pain points.)

Done since: the shared `win-common` crate (2026-11-13, Slice B —
the JSON engine, SHA-256 and FFI helpers consolidated; see
`crates/win-common/`), and runnable examples for every kit plus
the generated-bindings pack release (2026-11-13, Slice C — see
`examples/` and `tools/bindings-pack.py`); and the VM
verification kit (2026-11-13, Slice D — `tools/vm-verify/`,
PAIN_POINTS #54).

## Open, from the original roadmap

- A shared `win-common` crate for the Win32 interop boilerplate
  several kits and apps currently carry individually. (Done
  2026-11-13 — see Next above.)
- A VM verification kit: reusable clean-machine verification for
  Windows projects. (Done 2026-11-13 — `tools/vm-verify/`.)
- A packaging kit: one-command packaging built on the release
  template. (Superseded outside this repo: the suite's packaging
  now lives in SeanPak.)

Roadmap items are intent, not commitments; priorities follow the
pain points in [`PAIN_POINTS.md`](PAIN_POINTS.md).
