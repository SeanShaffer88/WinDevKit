# WinDevKit

Shared development resources for Sean's Windows desktop software —
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

## The Windows DLL Collection (33 kits)

33 small, zero-dependency DLLs that each do one common Windows job —
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

## License

MIT.
