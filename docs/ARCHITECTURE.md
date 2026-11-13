# Architecture

## Repository layout

- `kits/` — the 36-kit Windows DLL library. Every kit is a
  standalone Rust crate (its own `Cargo.toml`, `src/`, `include/`
  header, tests, README and LICENSE) exposing one small C ABI with
  JSON in and out. Kits do not depend on each other; they may share the first-party foundation crate `crates/win-common` (the family JSON engine, SHA-256 and FFI string helpers, maintained once — PAIN_POINTS #53).
- `tools/` — the developer tools: the quality gate
  (`gate.sh` / `gate.ps1`, and `gate-kits.sh` for the whole
  collection), the hardened GitHub publisher (`publish.py`), the
  DLL scaffolder (`scaffold-dll.py`), the verification runner
  (`verify.py`), fixture tooling and release-evidence helpers.
- `templates/` — copy-into-a-project templates: canonical CI and
  release workflows, a DLL skeleton, app manifests, checklists,
  design tokens and the accessibility explain pattern.
- `schemas/`, `examples/`, `tests/` — JSON schemas, worked
  examples, and the test suite for the Python tools (run by the
  root `python-tests` workflow).
- `docs/` — project documentation, including
  [`PAIN_POINTS.md`](PAIN_POINTS.md) (why every resource exists)
  and [`CATALOG.md`](CATALOG.md) (the kit catalog).

## How the pieces fit

- **Pain-point driven.** Every tool and template exists because of
  a named incident recorded in `docs/PAIN_POINTS.md`. New
  resources start with a pain-point entry, not just an idea.
- **One canonical kit pattern.** Each kit follows the same shape:
  zero-external-dependency Rust where feasible, a panic-proof C ABI, a
  header in `include/`, the same gate steps, and the same release
  package (DLL + import lib + header + LICENSE + README).
- **Gates before merges.** A kit change is gated by the canonical
  steps — format check, clippy with warnings denied, the full test
  suite, and a release build — run locally by `tools/gate.sh` and
  in CI by the root workflow.
- **Monorepo CI.** `.github/workflows/kits-ci.yml` runs one matrix
  job per kit on Windows whenever anything under `kits/` changes.
  Five kits carry extra steps inherited from their standalone CI:
  EmbedKit and OCRKit fetch pinned, hash-verified engine files and
  run end-to-end proofs; UpdateKit runs an end-to-end update
  pipeline; ArchiveKit and ImageKit run a native-interop check
  against the built DLL.
- **Monorepo releases.** `.github/workflows/kits-release.yml`
  releases one kit per run (by tag or manual dispatch): build with
  the kit's static-CRT configuration, package the historical zip,
  write `SHA256SUMS.txt`, attach both to the GitHub Release.
- **Static CRT throughout.** Every kit's `.cargo/config.toml`
  sets `+crt-static` for the MSVC targets, so shipped DLLs carry
  their C runtime instead of depending on a separate install.
  Native sub-builds must match — OCRKit's CMake engine stack is
  configured for the static runtime in its `build.rs`.
