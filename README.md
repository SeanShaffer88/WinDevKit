# WinDevKit

Shared development resources for Sean's Windows desktop software —
the tools, templates, and checklists that every project kept re-inventing.
Built from real friction: each item maps to a failure or delay that
actually happened (see [`docs/PAIN_POINTS.md`](docs/PAIN_POINTS.md)).

## What's here (v0.1)

**Tools**
- `tools/fixtures.py` — create disposable filesystem test data and verify exact
  removals or restoration using SHA-256 manifests. See [usage and limits](docs/FIXTURES.md).
- `tools/gate.sh` / `tools/gate.ps1` — the full local quality gate:
  fmt, clippy on **both** host and `x86_64-pc-windows-msvc` targets,
  the **full** test suite, windows check on all targets. Every step is
  annotated with the failure it has caught.
- `tools/publish.py` — publish files to GitHub via the Contents API,
  safely: plain content (never base64), per-file calls, ~105 KB size
  guard, workflow-path refusal with the reason, automatic SHA handling,
  and SHA-256 read-back verification. `--dry-run` and `--files-from git`.
- `tools/scaffold-dll.py` — start a new DLL in the house style
  (WinRecovery pattern) in one command.

**Templates**
- `templates/ci.yml` — canonical windows-latest CI (add via browser UI;
  the GitHub App can't write workflow files).
- `templates/dll-skeleton/` — zero-dependency Rust cdylib skeleton:
  panic-proof FFI, thread-local last-error, JSON helpers, `#[link]`-
  annotated platform layer, C header.
- `templates/app-manifests/` — per-monitor-v2 DPI, long-path aware app
  manifest + dependency-free embed snippet.
- `templates/checklists/` — on-machine verification and release lists.
- `templates/design/command-deck-tokens.json` — the chosen house design
  direction as portable tokens.
- `templates/a11y/explain-pattern.md` — the tooltip/accessible-name
  pattern distilled from InstallScope's P0-1 work.

## Roadmap (proposed, in leverage order)

1. **Shared Rust core — scaffold adoption implemented.** Optional WinCommon
   vendoring now supplies JSON/FFI helpers in new DLLs. Existing DLL migrations
   remain separate consumer changes; keep platform bindings local and verify
   public ABI behavior per adoption.
2. **Reusable GitHub workflow** — point every repo's tiny caller workflow
   at one versioned workflow here, so gate changes land once. (Needs the
   workflows-permission/browser step per repo, one time each.)
3. **App skeleton** — like the DLL skeleton but for a full Rust Win32 app:
   Command Deck theme, settings with golden-file tests, error dialog with
   fix paths, `explain` wired in, manifest + icon embedded.
4. **VM verification kit** — a scripted Windows VM setup (snapshot points,
   test-data seeding, smoke scripts per project) so the on-machine
   checklist takes an hour, not a day, and actually gets run.
5. **Packaging kit** — canonical NSIS + PortableApps templates, checksum/
   SBOM generation, signing checklist.
6. **Project catalog page** — one living index of all repos: CI status,
   verification status, next step. (Today that knowledge lives in memory
   files and chat threads.)

## License

MIT.

## Reusable foundation workflow

Start with [the current repository catalog and adoption plan](docs/REUSABLE_FOUNDATIONS.md).
The highest-leverage pieces are the shared gates/scaffolds here and WinCommon's
small Rust core; larger feature libraries are adopted per consumer.

```sh
python tools/scaffold-dll.py --name ExampleKit --prefix ek --out ../ExampleKit \
  --with-win-common ../WinCommon
cd ../ExampleKit
cargo generate-lockfile --offline
cargo fmt --all
bash ../WinDevKit/tools/gate.sh
```

`--with-win-common` is optional. It vendors source/license files and a SHA-256
inventory, adds a local path dependency, and uses the shared JSON/error/ownership
helpers. It needs a reviewed WinCommon checkout containing the hardened unsafe
raw-pointer API. No external runtime DLL or build-time download is added.
Omit the option for the standalone std-only skeleton. Generated AGENTS.md carries
the engineering and evidence-led alternative-recommendation policy forward. Names/prefixes are validated
before output creation; descriptions are escaped for TOML.

The full gate now fails if the Windows target is missing, covers the entire
workspace and respects the lockfile. `--quick` / `-Quick` explicitly reports a
**partial host check**, never a full GREEN result. Release FFI templates enable
unwinding so the included guard can catch Rust panics; invalid pointers and
allocation failures remain outside that protection. Source changes do not
retroactively update copies already held by other repositories.

For competitor-inspired features, use the [REA workflow](docs/REA_WORKFLOW.md).
The first review includes Ueli/Cerebro source snapshots and explicitly partial
REA evidence; it does not claim completed semantic analysis in this environment.

## Tool verification

```sh
python -m unittest discover -s tests -v
bash -n tools/gate.sh
```

18 tests cover missing-target/command failures, workspace/lockfile gating, scaffold
validation and a real generated Rust project's debug/release panic containment,
optional vendoring and hashes, publisher failure/read-back handling, and REA
partial-evidence reporting. Mocked publisher tests make no GitHub writes.

Separately, standalone and real WinCommon-backed smoke projects passed the full
host/Windows-target gate and debug/release tests locally. PowerShell changes
were source-reviewed but could not run here because `pwsh` is unavailable.
Native Windows linking/runtime verification remains a CI/on-machine gate.
The legacy publisher still requires its documented Muse connector CLI; GitHub
plugin callers should use the current connector directly rather than assuming
that executable is installed. No live run of the legacy publisher is claimed.

Developer tooling requires Python 3.11+ and a Rust toolchain with rustfmt/clippy.
The shared-crate option uses Python’s standard-library TOML reader.

## DLL consumer collection

Use the [13-project consumer index](docs/DLL_COLLECTION.md) and [machine-readable contracts/provenance](docs/DLL_COLLECTION.json) to distinguish source, native evidence, external engines/models and validated downloads. FastSearch is the first packaged Windows x64 pilot; WinCommon is a Rust helper, not a callable DLL.
