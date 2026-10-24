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
   files and chat threads.)

## Expansion (approved 2026-10-21, in build order)

Thirteen additions, each mapped to a named pain point in
`docs/PAIN_POINTS.md` (#13–#25). They build after the DLL collection's
publish queue drains. New DLLs join the collection and follow the
house pattern (Rust, C ABI, gate + CI proof, MIT).

Phase A — foundation: **SettingsKit** ✅ SHIPPED 2026-10-23
(SeanShaffer88/SettingsKit, CI green — versioned settings with
migrations), **LogKit** (one structured logging format), **GoldenKit**
(golden-file test crate + bless tool), **ProcessKit** (child-process
supervision), **JobKit** (progress/ETA/cancellation engine),
**AppHost** (app skeleton pre-wiring SettingsKit + LogKit + UpdateKit
+ CrashKit).

Phase B — capability: **ReleaseKit** (one-command releases),
**screenshot harness** (walks a CAPTURE.md list into README-ready
images), **NetKit** (hardened HTTP client), **ShellKit** (context
menus, associations, jump lists), **NotifyKit** (toasts),
**MediaKit** (media probing + thumbnails), **SignKit** (Authenticode
sign/verify; signing half waits on a certificate decision).

## License

MIT.
