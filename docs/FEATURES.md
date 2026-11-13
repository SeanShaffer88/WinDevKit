# Features

What WinDevKit provides, by area. Everything here is free and MIT
licensed.

## Developer tools (`tools/`)

- **Quality gate** — `gate.sh` / `gate.ps1` run the full local
  gate for a Rust Windows crate: format check, clippy on both the
  host and the Windows MSVC target, the full test suite, and a
  Windows check on all targets. Every step is annotated with the
  failure it exists to catch. `gate-kits.sh` runs the same gate
  across every kit in the collection and reports failures per kit.
- **Hardened GitHub publisher** — `publish.py` publishes files via
  the Contents API with plain (never base64) content, a size
  guard, workflow-path refusal, automatic SHA handling and
  SHA-256 read-back verification, plus a dry-run mode.
- **DLL scaffolder** — `scaffold-dll.py` starts a new DLL in the
  house style in one command.
- **Verification runner** — `verify.py` checks a project against
  recorded expectations, offline.
- **Fixtures and release evidence** — `fixtures.py` builds and
  checks filesystem fixtures; `release-evidence.py` and
  `rea-summary.py` assemble release verification evidence.
- **Catalog generator** — `catalog.py` generates the collection
  catalog (`docs/CATALOG.md`) from the kits' own folders and
  versions and checks it in CI, so the catalog cannot promise
  downloads that do not exist.

## Templates (`templates/`)

- Canonical CI (`ci.yml`) and release (`release.yml`) workflows
  for Rust Windows projects; the release template packages the
  DLL zip and its `SHA256SUMS.txt`.
- A zero-dependency Rust cdylib skeleton with panic-proof FFI,
  thread-local last-error and a C header.
- App manifests (per-monitor-v2 DPI, long-path aware), release
  and on-machine verification checklists, design tokens, and the
  accessibility explain pattern.

## The kit library (`kits/`)

34 small Windows DLLs, each doing one common job behind a small
C ABI with JSON in and out — archives, thumbnails, notifications,
settings, folder watching, OCR, shell integration, registry,
updates, and more. Browse [`CATALOG.md`](CATALOG.md) for the full
list with one-line descriptions. Every kit builds with the static
C runtime and is gated by the root `kits-ci` workflow.

## Schemas and examples

`schemas/` holds the JSON schemas the tools validate against;
`examples/` holds worked examples of the tools and templates in
use.
