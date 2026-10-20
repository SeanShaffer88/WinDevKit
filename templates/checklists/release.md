# Release Checklist

- [ ] `tools/gate.sh` green (fmt, clippy BOTH targets, full test suite)
- [ ] CI green on windows-latest for the exact commit being released
- [ ] On-machine checklist run for headline features (or the release notes
      name what is NOT VERIFIED — no silent gaps)
- [ ] Version bumped in Cargo.toml + header/about + CHANGELOG entry
- [ ] README claims re-read against reality (features, limits, sizes)
- [ ] License file present and correct (MIT for Sean-owned projects;
      bundled-component attributions kept — e.g. PortableApps/NSIS)
- [ ] Release artifacts built from the tagged commit: binary/DLL + .lib,
      SHA-256 checksums file attached
- [ ] Clean-machine smoke: install/run on a machine (or VM) without the
      dev toolchain — no missing-DLL surprises
- [ ] GitHub release notes: what changed, verification status, known limits
- [ ] Tag pushed; release marked latest only after the asset check passes
