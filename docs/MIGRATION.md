# Migration guide — the kit monorepo merge (2026-11-01)

On 2026-11-01 the 34 standalone kit repositories were merged into
this repository. Each kit now lives in its own folder under
[`kits/`](../kits/), with its source, header, tests and docs intact,
plus its own README and LICENSE.

## What changed

- **One home.** Kit source, issues and future releases live here,
  in WinDevKit, instead of in 34 separate repositories.
- **The old repositories are archived.** They are read-only: their
  code, history and releases stay exactly as they were, and every
  existing download link keeps working. Nothing was deleted.
  **Update (2026-11-12):** most of the standalone repositories were
  later deleted outright, which broke the catalog's download links.
  Every kit in the collection was therefore re-released from this
  repository (2026-11-12), and the catalog now points only at this
  repository's Releases, with a CI-checked generator keeping it
  that way. A handful of family repositories that were never merged
  (DocConvert, SQLiteSuperBuild, Whisper, WinRecovery, WinUIHelpers)
  are still live and are listed separately in the catalog.
- **CI moved to the root.** GitHub only runs workflows from a
  repository's root, so each kit's own workflow files (kept inside
  its folder for reference) no longer run. The live gate is the
  root `kits-ci` workflow — one job per kit, same checks as before —
  with `tools/gate-kits.sh` as the local equivalent.
- **Releases come from here now.** Future kit releases are cut from
  this repository with the root `kits-release` workflow — one kit at
  a time (tag form: `<Kit>-v<Version>`, e.g. `WatchKit-v0.2.1`), or
  the whole collection in a single dispatch (`ALL`).
  The zip contents and names are unchanged, and each release now
  also carries a `SHA256SUMS.txt`.
- **Static CRT.** Kits built from this repository link the static
  C runtime (each kit's `.cargo/config.toml` sets `+crt-static`),
  so the DLLs no longer need a separate VC++ runtime install.
  Release zips published earlier from the standalone repositories
  predate this change.

## What did not change

- Kit APIs and ABIs are untouched — the merge moved files, it did
  not modify kit code.
- Each kit keeps its name, its folder, its README and its MIT
  license.
- Existing release zips were available from the archived
  repositories until their deletion (see the update above); the
  current downloads are this repository's Releases.

## If you used a standalone kit repo

- Star/watch this repository instead — it is the kits' home now.
- File kit issues here, naming the kit in the title.
- To build a kit, clone this repo and build inside
  `kits/<KitName>/` exactly as you built the standalone repo.
