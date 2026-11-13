# Audit — verification state

A summary of how WinDevKit is checked, and what state those
checks were in at the last full pass. Detail lives in
[`VERIFICATION.md`](VERIFICATION.md),
[`WINDOWS_VALIDATION.md`](WINDOWS_VALIDATION.md) and
[`RELEASE_EVIDENCE.md`](RELEASE_EVIDENCE.md).

## What is checked

- **Every kit, every change under `kits/`:** the root `kits-ci`
  workflow runs one Windows job per kit — format check, clippy
  (warnings denied), the full test suite, and a release build —
  plus per-kit extras: engine fetch + end-to-end proofs for
  EmbedKit, OCRKit and UpdateKit, and native-interop checks for
  ArchiveKit and ImageKit.
- **The Python tools:** the root `python-tests` workflow runs the
  `tests/` suite.
- **Locally:** `tools/gate.sh` per crate, `tools/gate-kits.sh`
  for the whole collection.
- **Field checks:** a PowerShell smoke-test pack exercises the
  shipped DLLs on a real Windows machine (safe, read-only or
  temp-folder checks per kit), plus two manual demos for the
  features a script cannot see (toast display, jump lists).

## State at the last full pass (2026-11-12)

- The catalog audit found most catalog download links dead (the
  standalone kit repositories had been deleted after the merge).
  The full collection was re-released from this repository, the
  catalog was rebuilt as a generated, CI-checked document
  (`tools/catalog.py`), and a final online link audit of the new
  catalog passed for every entry.
- BridgeKit v0.2.0's grammar was verified against all 33 shipped
  kit headers: every header parses and generates, and the
  generated bindings compile together in C# and in Rust.
- The Python tools' suite, including the new catalog checks,
  passes locally and in the `python-tests` workflow.

## State at the previous full pass (2026-11-01)

- `kits-ci` on the merged tree: **34/34 jobs green**, both before
  and after the static-CRT template pass. The first static-CRT
  run caught one real defect — OCRKit's CMake engine stack was
  built for the dynamic CRT and failed to link — which was fixed
  and re-verified in the follow-up run.
- Every published file in the merge and the conformance passes
  was read back and compared byte-for-byte after upload.
- `kits-release` exercised end to end: OCRKit v0.1.1 released
  from this repository, its zip re-downloaded and verified
  against the attached `SHA256SUMS.txt`.
- Field evidence: the 2026-10-28 smoke run (116/116) and manual
  demos verified the collection's earlier builds on a real
  machine, and the static-CRT OCRKit v0.1.1 DLL passed its field
  test on a real machine on 2026-11-01 (hash match, DLL loads,
  engine responds).

## Known gaps

- The remaining kits' static-CRT builds are CI-verified but have
  not yet had field runs; each is checked as it is re-released
  from this repository.
- Kit behavior beyond what CI and the smoke pack exercise (for
  example, shell integration applied under a real application's
  identity) is verified per kit as noted in each kit's README.
