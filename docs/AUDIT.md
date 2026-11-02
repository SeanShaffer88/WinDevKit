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

## State at the last full pass (2026-11-01)

- `kits-ci` on the merged tree: **34/34 jobs green**, both before
  and after the static-CRT template pass. The first static-CRT
  run caught one real defect — OCRKit's CMake engine stack was
  built for the dynamic CRT and failed to link — which was fixed
  and re-verified in the follow-up run.
- Every published file in the merge and the conformance passes
  was read back and compared byte-for-byte after upload.
- Field evidence predates the merge: the 2026-10-28 smoke run
  (116/116) and manual demos verified the collection's earlier
  builds on a real machine.

## Known gaps

- The static-CRT kit builds are CI-verified but have not yet had
  a field smoke re-run; that needs a kit release from this repo
  plus a run of the smoke pack against it.
- The `kits-release` workflow has not yet cut a release; its
  first run is the remaining unproven path.
- Kit behavior beyond what CI and the smoke pack exercise (for
  example, shell integration applied under a real application's
  identity) is verified per kit as noted in each kit's README.
