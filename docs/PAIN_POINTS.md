# Pain Points This Kit Exists to Kill

Each resource in WinDevKit maps to friction actually observed across
Sean's projects (Oct 2026), not hypothetical best practice.

| # | Recurring pain | Where it bit | Resource |
|---|---|---|---|
| 1 | Re-writing the same publish helper per project; base64 blob incident; 105 KB argv ceiling; stale-SHA failures | ModernFlyouts PR #1/#2, InstallScope cli.rs split | `tools/publish.py` (plain content, size guard, SHA fetch, read-back verify) |
| 2 | Host clippy can't see `cfg(windows)` code → CI-only lint failures | WinRecovery CI run #1 | `tools/gate.sh` / `gate.ps1` (clippy on BOTH targets) |
| 3 | check/clippy don't link → LNK2019 surprises in CI | WinRecovery runs #2/#3 (missing `#[link]` import libs), SafeReturn S0.5 LNK2019 | gate docs + canonical CI with real release build; DLL skeleton pre-wires `#[link]` |
| 4 | Filtered local test gates miss golden-fixture failures | InstallScope PR #11 | gate runs the FULL suite, always |
| 5 | CI workflow re-created per repo, always via browser (App lacks Workflows permission) | DriverGuard, SafeReturn, ReelDeck, FileWeaver, WinRecovery | `templates/ci.yml` (one canonical file) |
| 6 | "UNVERIFIED on a real machine" lists growing in every project | SafeReturn S0.5/S3/S4, WinRecovery, InstallScope SR/DPI | `templates/checklists/on-machine-verification.md` |
| 7 | Win32 interop boilerplate (wide strings, registry, SCM, dynamic DLL loads) rewritten per project | InstallScope platform/windows.rs, DriverGuard dg-win, WinRecovery | WinRecovery.dll itself + DLL skeleton patterns; future `win-common` crate (roadmap) |
| 8 | Tooltip/a11y coverage gaps discovered by audit, fixed page by page | InstallScope P0-1 phases 1–11 | `templates/a11y/explain-pattern.md` |
| 9 | Design direction re-explained per project | InstallScope Command Deck | `templates/design/command-deck-tokens.json` |
| 10 | Manifest/DPI/long-path setup redone (or forgotten) per app | multiple | `templates/app-manifests/` |
| 11 | Release steps re-derived per project | all | `templates/checklists/release.md` |
| 12 | Starting each new DLL from a blank cargo project | DLL collection #1 took a full session to scaffold | `tools/scaffold-dll.py` + `templates/dll-skeleton/` |
| 13 | Default gate printed GREEN while missing Windows checks; workspace/lockfile coverage not enforced | Found while validating FastSearch in this session | strict full gate, explicit partial quick mode, behavioral shell tests |
| 14 | Publisher ignored SHA-related error text and treated unavailable read-back verification as deferred success | `tools/publish.py` review in this session | nonzero/structured-error handling, failed verification is nonzero, mocked write/read-back tests |
| 15 | New FFI skeleton combined catch_unwind claims with panic=abort and did not supply a panic guard | FastSearch release-profile and scaffold review | unwind-enabled template and real debug/release scaffold tests |
| 16 | Shared helpers existed but no new-project path actually consumed them; copied implementations multiplied | WinCommon status and scaffold review | opt-in reviewed WinCommon vendoring with source file hashes |
| 17 | REA process-ownership failure returned a large partial inventory that could be mistaken for completed source analysis | Ueli/Cerebro analysis in this session | `rea-summary.py`, explicit partial status and evidence/limitation preservation |

| 18 | Repeated manual verification commands, lost results between sessions, broken copied Git worktree pointer | InstallScope continuation, 2026-10-21 | tools/verify.py (checkpointed evidence; no cached passes) |
