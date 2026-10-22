# Windows integration evidence — October 21, 2026

Environment: Windows 11 Home build 26300, x64, standard user; Python 3.15 and the installed Rust MSVC toolchain. Reviewed toolkit source: `e3f622de68b2e4ff2ff0a1cd8e14f441076844f6` (PRs #1–#3 integrated).

- `python -m unittest discover -s tests -v`: 36 cases, 34 passed and two explicitly skipped symlink tests because this session could not create those links. Expected-failure fixtures printed failure evidence while their assertions passed; the suite exited successfully.
- Created a fresh inert filesystem fixture and ran `tools/fixtures.py check`: passed, no missing, added or changed entries. No deletion/cleanup application was run against the fixture.
- Ran the full `tools/verify.py` profile offline on the reviewed FastSearch integration commit `bbf4c701418e568b0585481bce87677285171e38`, explicitly requesting `x86_64-pc-windows-msvc`: **passed**. Formatting, strict host lint, 32 tests, doctests, host build, target lint/check, and source-stability evidence completed. Full logs and the versioned report remain local because they contain machine paths.
- Generated a disposable DLL scaffold with `--with-win-common` pointing to the reviewed WinCommon merge commit `45f965b3a03ce2163a8a191ee3185ff4d632c0e4`. Offline lockfile generation, strict Clippy, two Debug tests, two Release tests, all-target Windows check and Release DLL build passed. Vendoring retained its license and source inventory. This is a tested scaffold integration, not a claim that an existing published portfolio DLL has adopted WinCommon.
- Hosted toolkit matrix on the combined PR head passed Windows and Linux with Python 3.11 and 3.15. Native Windows checks here complement that matrix; they do not establish ARM64, recovery, accessibility or hostile-filesystem containment.

The Windows test harness now explicitly selects installed Git Bash where available instead of accidentally selecting a WSL launcher without a configured distribution. Scripts use LF endings. These corrections are included in the merged toolkit source.

Keep fixture manifests and verification reports local by default. Fixtures are bounded synthetic data; they cannot sandbox an uninstaller or certify disk recovery. See [fixture limits](FIXTURES.md) and [verification semantics](VERIFICATION.md).
