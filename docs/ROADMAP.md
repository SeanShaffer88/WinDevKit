# Roadmap

## Done

- The 34-kit DLL collection, built out from the approved
  expansion and field-verified end to end on a real Windows
  machine (smoke pack 116/116 plus both manual demos,
  2026-10-28).
- Download releases for every kit (from the standalone
  repositories, now archived; their releases remain live).
- The collection catalog (`docs/CATALOG.md`).
- The monorepo merge (2026-11-01): one repository, one CI gate
  (`kits-ci`, 34/34 green), one release workflow (`kits-release`),
  static-CRT builds for every kit.

## Next

- First kit release cut from the monorepo via `kits-release`,
  proving the tag-to-release path end to end.
- A field smoke-test re-run against the static-CRT builds (the
  2026-10-28 field pass covered the earlier dynamic-CRT builds;
  the static-CRT builds are CI-verified, including end-to-end
  proofs, but not yet field-run).

## Open, from the original roadmap

- A shared `win-common` crate for the Win32 interop boilerplate
  several kits and apps currently carry individually.
- A VM verification kit: reusable clean-machine verification for
  Windows projects.
- A packaging kit: one-command packaging built on the release
  template.

Roadmap items are intent, not commitments; priorities follow the
pain points in [`PAIN_POINTS.md`](PAIN_POINTS.md).
