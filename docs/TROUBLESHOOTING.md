# Troubleshooting

Real failure modes observed in this repository, and their fixes.

## A kit's CI did not run after my change

GitHub only runs workflows from the repository root. The
workflow files inside each kit's folder are kept for reference
and never run. Kit changes are gated by the root `kits-ci`
workflow, which triggers on changes under `kits/` — a change
that touches only docs or tools will not start it. You can also
run it manually from the Actions tab.

## Link errors: unresolved `__imp_*` symbols (LNK2019 / LNK1120)

A native sub-build was compiled for the dynamic C runtime
(`/MD`) while the Rust side links the static runtime
(`+crt-static` from the kit's `.cargo/config.toml`). The fix is
to build the native code with the static runtime too. OCRKit's
engine stack hit exactly this; its `build.rs` now passes
`CMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded` (with
`CMAKE_POLICY_DEFAULT_CMP0091=NEW`) to every CMake configure.

## OCRKit keeps using a stale engine build

The engine stack is built once per target directory and reused
(a marker file records completion). To force a rebuild, delete
the `ocrkit-engine` folder inside the kit's `target` directory
and build again.

## gate.sh says the Windows target is missing

A full gate run needs the `x86_64-pc-windows-msvc` target:
`rustup target add x86_64-pc-windows-msvc`. For a partial,
host-only check, run `tools/gate.sh --quick` — it says clearly
that the Windows checks were not run.

## publish.py refuses a file

By design: it refuses workflow paths (`.github/workflows/` must
go through the GitHub web UI — the API token lacks the
Workflows permission) and files over its ~105 KB size guard.
Both refusals print the reason; split the file or use the web
UI as directed.

## Windows warns about an unsigned binary

All binaries here are unsigned (no code-signing certificate).
SmartScreen may warn the first time a downloaded DLL or tool
runs; verify the file against the release's `SHA256SUMS.txt`
and choose "run anyway" if you trust the source.
