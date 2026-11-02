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
- First kit release cut from the monorepo: OCRKit v0.1.1
  (2026-11-01), its assets re-downloaded and hash-verified.
- Field check of a static-CRT build: the OCRKit v0.1.1 DLL
  passed its field test on a real Windows machine (2026-11-01) —
  the download matched its published SHA-256 sum, the DLL loads
  and reports its version, and the OCR engine responds with a
  real engine error when its language data is absent.

## Next

- Field smoke re-runs for the remaining kits' static-CRT builds,
  as each kit is re-released from the monorepo (the 2026-10-28
  field pass covered the earlier dynamic-CRT builds).

## Open, from the original roadmap

- A shared `win-common` crate for the Win32 interop boilerplate
  several kits and apps currently carry individually.
- A VM verification kit: reusable clean-machine verification for
  Windows projects.
- A packaging kit: one-command packaging built on the release
  template.

Roadmap items are intent, not commitments; priorities follow the
pain points in [`PAIN_POINTS.md`](PAIN_POINTS.md).
