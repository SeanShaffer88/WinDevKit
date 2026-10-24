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
| 13 | Settings load/save hand-rolled per app; a default flip silently breaks golden files; no schema versioning or migrations anywhere | InstallScope PR #11 (golden failure), every app's settings code | **SettingsKit** (DLL, expansion #1) — ✅ SHIPPED 2026-10-23, SeanShaffer88/SettingsKit, CI green |
| 14 | Logging reinvented per app in incompatible formats; a milestone log had to be bolted on after a launch-failure hunt | ytTrayDL `yttraydl.log`, CrucibleKit `cruciblekit.log`, InstallScope logs | **LogKit** (DLL, expansion #2) |
| 15 | Golden-file testing re-derived per project, fixtures managed by hand | InstallScope settings/job goldens | **GoldenKit** (crate + bless tool, expansion #3) |
| 16 | Child-process supervision redone per app; orphaned/hung children handled ad hoc | yt-dlp + ffmpeg (ytTrayDL), NSIS + PortableApps launcher (InstallScope) | **ProcessKit** (DLL, expansion #4) |
| 17 | Progress % + ETA demanded by the master prompt but implemented per job, per app | InstallScope jobs, MuseDesktop downloads | **JobKit** (DLL, expansion #5) |
| 18 | App plumbing (single-instance, tray, settings, logging, updates, crash capture) rebuilt for every new tool | MuseDesktop and ytTrayDL both hand-wired all of it | **AppHost** (app skeleton, expansion #6) |
| 19 | Release machinery rebuilt per project; checklists exist (pain #11) but execution is manual every time | InstallScope release.yml + SHA256SUMS, XToolbox and ytTrayDL releases | **ReleaseKit** (tool, expansion #7) |
| 20 | README screenshot capture lists prepared but captures wait on manual sessions, project after project | ytTrayDL `docs/screenshots/CAPTURE.md`, SafeReturn S6 capture list | **Screenshot harness** (tool, expansion #8) |
| 21 | HTTP transport hand-rolled per consumer, starting with a from-scratch WinHTTP layer | UpdateKit `uk_download` | **NetKit** (DLL, expansion #9) |
| 22 | Shell integration done as raw registry edits; a rename had to chase verbs, associations, and uninstall keys by hand | Expunge→InstallScope rename | **ShellKit** (DLL, expansion #10) |
| 23 | No house way to raise a notification; approval alerts needed a whole separate userscript project | muse-allow-alerter | **NotifyKit** (DLL, expansion #11) |
| 24 | Media files probed by shelling out to external tools just to learn duration/codecs/streams | ReelDeck pipeline | **MediaKit** (DLL, expansion #12) |
| 25 | Every release ships unsigned; no signing or signature-verification helper exists | InstallScope v0.1.0, MuseDesktop v0.1.0, ytTrayDL installer | **SignKit** (DLL, expansion #13) |
