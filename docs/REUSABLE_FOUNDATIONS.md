# Reusable Windows foundations

Review date: October 21, 2026. Source: current repositories and their default-branch
READMEs; detailed code review in this batch covered WinDevKit, WinCommon and
FastSearch. A listed capability is not a blanket production-readiness claim.
InstallScope and forked repositories are excluded from implementation work.

## Build first, reuse selectively

| Repository | Useful across projects | Decision and current boundary |
|---|---|---|
| [WinDevKit](https://github.com/SeanShaffer88/WinDevKit) | Scaffolds, gates, release/a11y checklists, publishing and research workflow | Primary development accelerator. This batch hardens gates/publisher, validates scaffolds and adds optional offline WinCommon vendoring. PowerShell needs a native Windows run. |
| [WinCommon](https://github.com/SeanShaffer88/WinCommon) | JSON, FFI ownership/error plumbing, UTF-16 and calendar helpers | Primary shared Rust core. Fixed default JSON construction and raw-pointer API safety; added checked UTF-16 input. 29 tests plus host/Windows-target gates pass locally; [core hardening PR](https://github.com/SeanShaffer88/WinCommon/pull/1). No public package publication is needed for vendoring. |
| [FastSearch](https://github.com/SeanShaffer88/FastSearch) | Indexed name search for Meridian, FileWeaver and launchers | Improved separately with prefix seeking, explicit filters, immutable FFI snapshots and index-input validation. Snapshot freshness/NTFS journal remains future work; no claim of live indexing. |
| [WinRecovery](https://github.com/SeanShaffer88/WinRecovery) | Inventory and Windows recovery primitives | Useful for DriverGuard/SafeReturn/system tools. Do not substitute portable compile checks for live restore/VSS tests. |
| [SQLiteSuperBuild](https://github.com/SeanShaffer88/SQLiteSuperBuild) | Search, operation ledgers, history and catalogs | Reuse pinned builds where a C ABI consumer needs them. Rust apps already using bundled SQLite should not carry a second engine without a reason. |
| [VaultKit](https://github.com/SeanShaffer88/VaultKit) | Local tokens and credentials | Adopt per consumer after account/namespace and Windows error-path tests. Do not store secrets in generic settings files. |
| [CrashKit](https://github.com/SeanShaffer88/CrashKit) | Local crash evidence and logs | Opt-in host integration; decide dump location, retention and disclosure in each app. Crash-path behavior requires native validation. |
| [UpdateKit](https://github.com/SeanShaffer88/UpdateKit) | Manifest checks and verified staged downloads | Useful later in packaged applications. Applying/restarting is a host responsibility; do not label the staged-download API a complete updater. |
| [ArchiveKit](https://github.com/SeanShaffer88/ArchiveKit) | ZIP/TAR import/export | Before broad untrusted-file adoption, prioritize parser/extraction fuzzing, resource limits and path/reparse-point tests. A custom codec is a maintenance obligation. |
| [ImageKit](https://github.com/SeanShaffer88/ImageKit) | Thumbnail/image transforms | Useful behind explicit supported-format and memory limits. Prioritize malformed-input differential/fuzz tests before expanding custom codecs. |
| [TimeKit](https://github.com/SeanShaffer88/TimeKit) | Zoned schedules and civil-time conversion | Current-rule engine has documented historical/Morocco limitations. It is not yet a historical-time oracle. Full TZif tables are the next correctness milestone. |
| [Whisper](https://github.com/SeanShaffer88/Whisper) | Optional local transcription | Feature-specific dependency, not a baseline for every application. Models/toolchain cost is justified only by a speech feature. |
| [OCRKit](https://github.com/SeanShaffer88/OCRKit) | Optional local OCR | Feature-specific; verify the actual engine-enabled build and language assets, not only stub-mode tests. |
| [EmbedKit](https://github.com/SeanShaffer88/EmbedKit) | Optional semantic search | Exact vector search and optional model/runtime integration; model distribution, memory and batching need host-specific evaluation. |
| [OfflineAICoding](https://github.com/SeanShaffer88/OfflineAICoding) | Tool orchestration/setup experience | Larger product and integration surface, not the shortest route to this batch's shared infrastructure goals. |
| [OpenWorker](https://github.com/SeanShaffer88/OpenWorker) | Potential development automation | Candidate for a dedicated architecture/security review. Not code-audited in this batch; no adoption or completion claim. |

## Recommended alternative to duplicated helpers

Use a **reviewed, hash-inventoried vendored WinCommon snapshot** in new Rust DLLs
when its helpers fit. This trades a small local path dependency for fewer
independent implementations; binaries still need no separate WinCommon DLL.
Keep the std-only standalone scaffold for cases where that tradeoff is unwanted.

This is distinct from claiming "zero dependencies" and "pure Rust" mean the same
thing. They do not. Likewise, for complex archive/image formats, evaluate an
established pure-Rust codec against the hand-maintained implementation before
extending it. Compare compatibility, malformed-input behavior, binary size,
licenses and measured throughput before changing a project's dependency policy.
No archive/image codec migration was made in this batch.

## New-project path

```sh
python WinDevKit/tools/scaffold-dll.py --name ExampleKit --prefix ek \
  --out ./ExampleKit --with-win-common ./WinCommon
cd ExampleKit
cargo generate-lockfile --offline
cargo fmt --all
bash ../WinDevKit/tools/gate.sh
cargo test --release --locked
```

The supplied WinCommon checkout must include the hardened raw-pointer API used
by the generated wrappers. `vendor/win-common/VENDORED.json` records source file
SHA-256 values and keeps source/license material alongside the dependency.
Review upstream updates, regenerate deliberately and rerun the consumer's gates;
do not silently replace the vendored copy during an ordinary build.

Full gate requires `x86_64-pc-windows-msvc`; missing target is a failure.
`--quick` is an explicitly partial host check. Neither is a substitute for a
native Windows release link, C ABI smoke test, runtime and accessibility tests.

## Avoid making every dependency a prerequisite

The fastest safe pipeline uses the small shared core immediately, then adopts
feature libraries only when an application needs them. Completing OCR, speech,
all codecs and a live NTFS index before another UI feature would delay delivery
without testing those components in a real consumer. The catalog records the
remaining gates instead of calling every library complete.
