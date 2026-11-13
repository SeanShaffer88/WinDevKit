# Changelog

Notable changes to WinDevKit as a whole. Individual kits also keep
their own release history; kit releases before 2026-11-01 were
published from the standalone kit repositories (now archived).

## 2026-11-12 — Collection re-released here; catalog made self-checking; BridgeKit grammar completed

- The standalone kit repositories the catalog linked to were
  deleted after the merge, leaving most catalog downloads dead.
  Every kit in the collection was re-released from this repository
  at its current version, and `docs/CATALOG.md` is now generated
  by `tools/catalog.py` from `docs/CATALOG_DATA.json` plus each
  kit's own `Cargo.toml` — every download points at this
  repository's Releases, and a CI test fails if the data and the
  tree disagree. The five family members that were never merged
  and whose repositories are still live are listed separately;
  FastSearch and HardwareInfo are honestly marked unpublished.
- `kits-release` can now release the whole collection in one
  dispatch (`ALL`), each kit at its own Cargo.toml version,
  skipping kits already released.
- BridgeKit v0.2.0: the header grammar now covers every type the
  collection's 33 shipped headers actually use — `int64_t`,
  `uint8_t`, `size_t`, `double`, scalar out-pointers and buffers,
  function-pointer typedefs (C# delegates, Rust aliases), concrete
  structs with array fields — after a survey found the original
  grammar failed on 14 of the 33 headers. Generated bindings for
  the whole collection compile together in C# and in Rust, and
  parameter names that collide with language keywords are escaped.
  Unknown types are still a hard error naming the token.
- OCRKit v0.1.2: the source version now matches its release line
  (the v0.1.1 release shipped a DLL reporting 0.1.0).
- README rebuilt as a front door: TL;DR, a five-minute quickstart,
  a which-kit decision table, and runnable SettingsKit examples
  (C# and Python) under `examples/`.
- Issue and pull-request templates added.

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
