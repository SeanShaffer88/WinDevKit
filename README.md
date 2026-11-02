# WinDevKit

Shared development resources for Windows desktop software —
the tools, templates, and checklists that every project kept re-inventing.
Built from real friction: each item maps to a failure or delay that
actually happened (see [`docs/PAIN_POINTS.md`](docs/PAIN_POINTS.md)).

## What's here (v0.1)

**Tools**
- `tools/gate.sh` / `tools/gate.ps1` — the full local quality gate:
  fmt, clippy on **both** host and `x86_64-pc-windows-msvc` targets,
  the **full** test suite, windows check on all targets. Every step is
  annotated with the failure it has caught.
- `tools/publish.py` — publish files to GitHub via the Contents API,
  safely: plain content (never base64), per-file calls, ~105 KB size
  guard, workflow-path refusal with the reason, automatic SHA handling,
  and SHA-256 read-back verification. `--dry-run` and `--files-from git`.
- `tools/scaffold-dll.py` — start a new DLL in the house style
  (WinRecovery pattern) in one command.

**Templates**
- `templates/ci.yml` — canonical windows-latest CI (add via browser UI;
  the GitHub App can't write workflow files).
- `templates/dll-skeleton/` — zero-dependency Rust cdylib skeleton:
  panic-proof FFI, thread-local last-error, JSON helpers, `#[link]`-
  annotated platform layer, C header.
- `templates/app-manifests/` — per-monitor-v2 DPI, long-path aware app
  manifest + dependency-free embed snippet.
- `templates/checklists/` — on-machine verification and release lists.
- `templates/design/command-deck-tokens.json` — the chosen house design
  direction as portable tokens.
- `templates/a11y/explain-pattern.md` — the tooltip/accessible-name
  pattern distilled from InstallScope's P0-1 work.

## Kit library (merged 2026-11-01)

The 34 kit repositories were merged into this repo on 2026-11-01. Each kit keeps its own folder under `kits/`, with its source, header, tests, docs, and its own README and LICENSE. Each kit's original `.github/workflows/` files are kept inside its folder for reference; they are not active workflows in this repo (GitHub only runs workflows from the root `.github/workflows/`). The collection's live CI is the root `kits-ci` workflow — one job per kit (local twin: `tools/gate-kits.sh`) — and future kit releases are cut from this repo with the root `kits-release` workflow. The original kit repos were archived read-only on 2026-11-01; they remain on GitHub as the historical record, including their releases. See [`docs/MIGRATION.md`](docs/MIGRATION.md).

- [ArchiveKit](kits/ArchiveKit/) — Create, list, test and extract ZIP and TAR archives from any language that can call C — zero dependencies, DEFLATE codec built in. DLL #3 in the Windows DLL Collection
- [BridgeKit](kits/BridgeKit/) — Verified C# and Rust binding generator for the DLL collection, generated from the kits' own headers. Zero-dependency Rust CLI tool.
- [ClipKit](kits/ClipKit/) — Clipboard text and file-list access plus change detection, over a JSON C ABI. Zero-dependency Rust DLL.
- [CrashKit](kits/CrashKit/) — DLL #10 of Sean's Windows library collection: crash capture (minidump + JSON sidecar) and structured logging behind a small C ABI (MIT)
- [DiagKit](kits/DiagKit/) — One-call diagnostics bundles (logs, dumps, versions, hashes) in a single zip with a JSON manifest. Zero-dependency Rust DLL, JSON in/out over a C ABI.
- [EmbedKit](kits/EmbedKit/) — Local semantic search behind one clean C ABI — text embeddings via runtime-loaded ONNX Runtime, cosine vector index built in. DLL #12 in the Windows DLL Collection.
- [FileMetaKit](kits/FileMetaKit/) — File metadata toolkit behind a small C ABI: read, edit and compare metadata across images, audio, video and documents (WinDevKit DLL #30)
- [FileOpsKit](kits/FileOpsKit/) — File operation engine behind a small C ABI: copy, move, rename and delete jobs with progress, cancellation, conflict policies, retries and undo (WinDevKit DLL #27)
- [FixtureKit](kits/FixtureKit/) — Deterministic test-fixture file generator (images, audio, archives, corrupt variants). Zero-dependency Rust DLL, JSON in/out over a C ABI.
- [ImageKit](kits/ImageKit/) — Image decode, transform, and encode behind one clean C ABI — PNG/BMP in pure Rust
- [InstanceKit](kits/InstanceKit/) — Single-instance mutex with named-pipe argument forwarding, over a JSON C ABI. Zero-dependency Rust DLL.
- [JobKit](kits/JobKit/) — Background-work engine behind a small C ABI — progress %, ETA, pause/resume, cooperative cancellation (WinDevKit DLL #20)
- [LinkKit](kits/LinkKit/) — Windows shortcut (.lnk) create, read and update including AppUserModelID, over a JSON C ABI. Zero-dependency Rust DLL.
- [LogKit](kits/LogKit/) — Structured, rolling, crash-safe logging in one house format behind a small C ABI (WinDevKit DLL #18)
- [MediaKit](kits/MediaKit/) — Pure-Rust media probing — duration, codecs and streams for WAV, MP3, FLAC, Ogg, MP4, Matroska and AVI (WinDevKit DLL #25)
- [NetKit](kits/NetKit/) — Hardened HTTP(S) client behind a small C ABI — policy-checked redirects and retries, size caps, digest-verified downloads, no cert bypass
- [NotifyKit](kits/NotifyKit/) — Tray notifications and balloon alerts without WinRT, plus a coalescing notification queue (WinDevKit DLL #24)
- [OCRKit](kits/OCRKit/) — Offline OCR behind one clean C ABI — vendored Tesseract engine, image in, text + confidence JSON out. DLL #13 in the Windows DLL Collection.
- [PDFKit](kits/PDFKit/) — Planned PDF library with a C ABI. Fixture-only foundation; no PDF engine or release published yet.
- [PathKit](kits/PathKit/) — Long-path and Unicode compatibility layer behind a small C ABI: path normalization, validation and conversion with plain-language errors (WinDevKit DLL #28)
- [ProcessKit](kits/ProcessKit/) — Child-process launch and supervision behind a small C ABI — captured output, timeouts, job-object tree kill, elevation rules (WinDevKit DLL #19)
- [ProviderKit](kits/ProviderKit/) — File provider adapter SDK behind a small C ABI: browse local disks, archives and custom providers through one interface (WinDevKit DLL #32)
- [RegKit](kits/RegKit/) — Registry read, write and list with undo manifests, over a JSON C ABI. Zero-dependency Rust DLL.
- [RenameKit](kits/RenameKit/) — Batch rename and transform engine behind a small C ABI: preview, validate and apply bulk renames with collision detection and rollback (WinDevKit DLL #31)
- [SettingsKit](kits/SettingsKit/) — Atomic settings files with schema versioning and migrations behind a small C ABI (WinDevKit DLL #17)
- [ShellInteropKit](kits/ShellInteropKit/) — Windows Shell interop wrapper behind a small C ABI: typed file info, icons, verbs and properties without raw shell boilerplate (WinDevKit DLL #34)
- [ShellKit](kits/ShellKit/) — Safe Windows shell integration — context-menu verbs, file associations, protocol handlers as plan + apply with backup (WinDevKit DLL #23)
- [SignKit](kits/SignKit/) — Authenticode inspection and verification helpers for PE files — verify only, no signing (WinDevKit DLL #26)
- [ThumbKit](kits/ThumbKit/) — Thumbnail and preview pipeline behind a small C ABI: pluggable generators, a bounded LRU cache and asynchronous retrieval (WinDevKit DLL #29)
- [TimeKit](kits/TimeKit/) — DLL #11 of Sean's Windows library collection: IANA timezones and civil time done correctly (DST gap/overlap-safe) behind a small C ABI (MIT)
- [UiProbeKit](kits/UiProbeKit/) — UI Automation inspection and actions (window and control trees, invoke, set value) over a JSON C ABI. Zero-dependency Rust DLL.
- [UpdateKit](kits/UpdateKit/) — Self-update behind one clean C ABI — version-checked manifest, verified downloads, staged packages
- [VaultKit](kits/VaultKit/) — DLL #9 of Sean's Windows library collection: secrets storage via DPAPI + Credential Manager behind a simple C ABI (MIT)
- [WatchKit](kits/WatchKit/) — Folder change and cache coordinator behind a small C ABI: coalesced change events and self-invalidating folder caches (WinDevKit DLL #33)

## The Windows DLL Collection (41 kits)

41 small, zero-dependency DLLs that each do one common Windows job —
folder watching, thumbnails, notifications, settings, archives, OCR,
speech-to-text and more — behind one shared C interface with JSON in and
out, each with a ready-to-use download. Browse the full list in
[**the collection catalog**](docs/CATALOG.md).

## AI-assist suite (shipped 2026-10-24)

Seven standalone tools (Python 3, standard library only, MIT) built from
the pain points in `docs/PAIN_POINTS.md` (#26–#32) — each exists to make
an AI development agent faster and less error-prone across this whole
project family:

- [PublishPilot](https://github.com/SeanShaffer88/PublishPilot) —
  publish preflight (size/base64/CRLF/execute-bit/workflow guards),
  manifest, and hash read-back verification.
- [RepoRadar](https://github.com/SeanShaffer88/RepoRadar) — cross-repo
  status snapshot plus SyncGuard, the pre-publish check that local HEAD
  matches live remote HEAD.
- [FieldVerify](https://github.com/SeanShaffer88/FieldVerify) —
  on-machine verification checklists run in one sitting, with an
  evidence bundle (results, report, logs) per run.
- [ContextPack](https://github.com/SeanShaffer88/ContextPack) — one
  compact, AI-ready brief per repo: stack, pinned versions, license read
  from the file itself, gate commands, docs.
- [CaptureKit](https://github.com/SeanShaffer88/CaptureKit) — CAPTURE.md
  screenshot specs: plan, generate the Windows capture script, wire
  captures into READMEs, verify none are missing.
- [ForAISearch](https://github.com/SeanShaffer88/ForAISearch) — local
  SQLite FTS5 search over the ForAI resource catalog
  (resources.json / resources.csv).
- [GateRunner](https://github.com/SeanShaffer88/GateRunner) — one
  gate.toml runs any stack's quality gate in order, with progress %,
  ETA, and warnings for known-dangerous gate patterns.

All seven are v0.1.0 (Latest) with CI green.

## Roadmap (proposed, in leverage order)

1. **`win-common` shared Rust crate** — wide strings, registry reader,
   hidden-process/PowerShell runner, known-folder paths, single-instance,
   elevation check: the code InstallScope, DriverGuard, SafeReturn and
   WinRecovery each carry a private copy of today. (WinRecovery.dll covers
   the *C-ABI* consumers; this covers the *Rust* apps.)
2. **Reusable GitHub workflow** — point every repo's tiny caller workflow
   at one versioned workflow here, so gate changes land once. (Needs the
   workflows-permission/browser step per repo, one time each.)
3. **App skeleton** — like the DLL skeleton but for a full Rust Win32 app:
   Command Deck theme, settings with golden-file tests, error dialog with
   fix paths, `explain` wired in, manifest + icon embedded.
4. **VM verification kit** — a scripted Windows VM setup (snapshot points,
   test-data seeding, smoke scripts per project) so the on-machine
   checklist takes an hour, not a day, and actually gets run.
5. **Packaging kit** — canonical NSIS + PortableApps templates, checksum/
   SBOM generation, signing checklist.
6. **Project catalog page** — one living index of all repos: CI status,
   verification status, next step. (Today that knowledge lives in memory
   files and chat threads.) The status/CI half of this is now covered by
   **RepoRadar** (see the AI-assist suite above); verification status
   and next steps remain open.

## Expansion (approved 2026-10-21, in build order)

Thirteen additions, each mapped to a named pain point in
`docs/PAIN_POINTS.md` (#13–#25). They build after the DLL collection's
publish queue drains. New DLLs join the collection and follow the
house pattern (Rust, C ABI, gate + CI proof, MIT).

Phase A — foundation: **SettingsKit** ✅ SHIPPED 2026-10-23
(SeanShaffer88/SettingsKit, CI green — versioned settings with
migrations), **LogKit** ✅ SHIPPED 2026-10-23 (SeanShaffer88/LogKit,
CI green — one structured logging format), **GoldenKit** ✅ SHIPPED 2026-10-24
(SeanShaffer88/GoldenKit, CI green — golden-file test crate + bless tool), **ProcessKit** ✅ SHIPPED 2026-10-24
(SeanShaffer88/ProcessKit, CI green — child-process supervision:
captured output, timeouts, Job Object tree kill, elevation rules), **JobKit** ✅ SHIPPED 2026-10-24
(SeanShaffer88/JobKit, CI green — background-work engine: progress %,
ETA, pause/resume, cooperative cancellation),
**AppHost** ✅ SHIPPED 2026-10-24
(SeanShaffer88/AppHost, CI green — app skeleton + generator pre-wiring
SettingsKit + LogKit + UpdateKit + CrashKit + ProcessKit + JobKit;
tray handled in the window procedure, single-instance by named mutex).

Phase B — capability: **ReleaseKit** ✅ SHIPPED 2026-10-24
(SeanShaffer88/ReleaseKit, CI green — plan / prepare / verify for
one-command releases; verify re-measures the live release and is the
ship gate),
**screenshot harness** ✅ COVERED 2026-10-24 by CaptureKit
(SeanShaffer88/CaptureKit — CAPTURE.md spec → capture walk script →
README wire/verify; a duplicate harness was deliberately not built),
**NetKit** ✅ SHIPPED 2026-10-24
(SeanShaffer88/NetKit, CI green — hardened HTTP client: policy-checked
redirects/retries, size caps, digest-verified downloads, no cert
bypass), **ShellKit** (context
menus, associations, jump lists), **NotifyKit** (toasts),
**MediaKit** (media probing + thumbnails), **SignKit** (Authenticode
sign/verify; signing half waits on a certificate decision).

## Project documents

- [Features](docs/FEATURES.md) — what the tools, templates and kits provide
- [Install and use](docs/INSTALL.md) — getting the kits and tools running
- [Architecture](docs/ARCHITECTURE.md) — repository layout and how CI/releases work
- [Compatibility](docs/COMPATIBILITY.md) — platforms, targets and runtimes
- [Migration](docs/MIGRATION.md) — the 2026-11-01 kit monorepo merge, explained
- [Changelog](docs/CHANGELOG.md) · [Roadmap](docs/ROADMAP.md) · [Audit](docs/AUDIT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md) · [Support](docs/SUPPORT.md) · [Security](docs/SECURITY.md)
- [Contributing](docs/CONTRIBUTING.md) · [Code of Conduct](docs/CODE_OF_CONDUCT.md) · [Governance](docs/GOVERNANCE.md) · [Maintainers](docs/MAINTAINERS.md) · [Credits](docs/CREDITS.md)

## License

MIT.
