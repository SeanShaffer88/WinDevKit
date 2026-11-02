# Contributing

Contributions are welcome — WinDevKit exists to be useful to
Windows developers generally, not just to its maintainer's own
projects.

## How to contribute

1. Open an issue first for anything larger than a small fix, so
   the shape of the change can be agreed before code is written.
2. Fork, branch, and open a pull request against `main`.
3. Keep each change focused: one kit, one tool, or one template
   per pull request where that is practical.

## House rules (they exist for recorded reasons)

- **New resources need a pain point.** Every tool and template in
  this repo maps to a real incident in
  [`PAIN_POINTS.md`](PAIN_POINTS.md). A proposal for a new
  resource starts with the friction it removes, added to that
  file in the same change.
- **The gate must pass.** Run `tools/gate.sh` in the crate you
  changed (or `tools/gate-kits.sh <KitName>` from the repo root)
  and include the result in the pull request. CI runs the same
  checks per kit and must be green.
- **Kits keep the canonical shape:** zero-dependency Rust where
  feasible, a panic-proof C ABI, the header in `include/`, tests
  in the crate, and the kit's own README kept accurate.
- **Docs are factual.** READMEs, changelogs and release notes
  describe the product as it is — no process commentary.
- **License.** Contributions are under the repo's MIT license.
