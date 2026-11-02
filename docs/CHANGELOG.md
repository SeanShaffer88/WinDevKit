# Changelog

Notable changes to WinDevKit as a whole. Individual kits also keep
their own release history; kit releases before 2026-11-01 were
published from the standalone kit repositories (now archived).

## 2026-11-01 — Monorepo merge and V2.0 kit conformance

- Merged the 34 standalone kit repositories into `kits/`, each kit
  intact in its own folder; the original repositories were then
  archived read-only (their releases and history remain live).
- Added root `kits-ci` workflow: one CI job per kit running the
  canonical gate steps, plus each kit's fetch / end-to-end /
  interop extras. Added `tools/gate-kits.sh` as its local twin.
- Added the static-CRT `.cargo/config.toml` (from CrucibleKit's
  proven configuration) to all 34 kits.
- Fixed OCRKit's CMake engine stack to build with the static CRT
  after the first combined run failed to link (dynamic-CRT
  `__imp_*` symbols); full collection re-verified 34/34 in CI.
- Added root `kits-release` workflow for per-kit releases from the
  monorepo (historical zip shape plus `SHA256SUMS.txt`), and
  updated `templates/release.yml` to emit `SHA256SUMS.txt`.
- Adopted the standard project document set in `docs/`.

## 2026-10-28 — Collection complete and field-verified

- Published the collection catalog (`docs/CATALOG.md`) covering
  all 33 then-current kits with download links.
- Shipped v0.2.0 upgrades: ThumbKit (built-in PNG/JPEG decoders),
  WatchKit (native ReadDirectoryChangesW backend), NotifyKit
  (WinRT toast backend), ShellKit (jump lists).
- Completed v0.1.0 download releases for every kit in the
  collection.
- Field verification on a real Windows machine: the smoke-test
  pack passed 116/116 checks, and both manual demos (toast
  display, jump-list round-trip) were confirmed — the whole
  collection field-verified end to end.

## 2026-10-24 — AI-assist suite

- Shipped the seven-tool AI-assist suite (PublishPilot, RepoRadar,
  FieldVerify, ContextPack, CaptureKit, ForAISearch, GateRunner)
  as MIT Python command-line tools with verified v0.1.0 releases.

## 2026-10-21 — WinDevKit v0.1

- Initial shared resources published: quality-gate scripts, the
  hardened GitHub publisher, the DLL scaffolder, canonical CI and
  release templates, app manifests, checklists, design tokens and
  the accessibility explain pattern — each mapped to a named pain
  point in `docs/PAIN_POINTS.md`.
- The 13-item kit expansion was approved and built out over the
  following week, completing the DLL collection.
