# Portable verification runner

Run from any directory with Python 3.10 or newer:

```sh
python /path/to/WinDevKit/tools/verify.py /path/to/project --offline
python /path/to/WinDevKit/tools/verify.py /path/to/project --doctor
python -m unittest discover -s tests -v
```

The runner reuses Cargo's incremental build cache. It runs formatting, host
Clippy, the full all-target test suite, doctests, a host build, and Clippy/check
for installed Windows targets. Commands run sequentially to avoid Cargo lock
contention. All Cargo dependency resolution is locked. It never installs tools,
downloads DLLs, changes source, repairs Git, publishes, or invokes a shell.
Cargo itself executes project build scripts and tests: only use full mode on
reviewed projects. Doctor mode runs Git/toolchain probes and fingerprints source without executing Cargo.

Strict warnings are the default. For a project with known warnings, explicitly
use `--allow-warnings`; the report records the relaxed policy and compiler logs
retain the warnings. This does not change tests. Use `--target TARGET` repeatedly
to request specific installed Windows targets. Missing requested targets fail;
automatically unavailable Windows coverage is labeled skipped. No cached test
result is accepted as a new pass.

Each invocation creates a unique evidence directory under the system temporary
directory, or under `--output PATH`. It contains per-step logs and versioned
`report.json`: project, toolchain, Git status, host, command arguments, durations,
exit codes, statuses, and platform limits. Completed steps are saved after each
command. Exit 1 means failed, timed out, or unavailable requested work; exit 0
can mean `passed_with_limits` or `inspection_only`, so inspect the status.
Evidence can contain local paths and compiler output; it stays local and is
never uploaded automatically. Delete evidence directories when no longer needed.

The default timeout is 900 seconds per command; adjust with `--timeout`.
Timeout terminates and waits for the direct command; descendant build tools may
survive. This runner is developer orchestration, not a process sandbox.

Cross-target checking does not link Windows executables. A Windows native build,
runtime workflows, accessibility, recovery, and release packaging remain separate
gates. Existing gate.sh/gate.ps1 and CI remain unchanged.

Timings describe this invocation only. They are evidence for future comparisons,
not proof that development or application performance has improved.

## Source provenance

Reports record a SHA-256 fingerprint of Git-listed tracked and nonignored
untracked files before and after the checks, together with the Git revision.
Content, file names, executable bits, deleted entries, and symbolic-link target
text contribute to the fingerprint. Changes during a run fail the source-stability
step. Broken Git, submodules, special entries, reparse files, or inventory limits
make this step explicitly skipped rather than claiming stable source.

Limits: 100,000 entries, 16 MiB of path inventory, 128 MiB of content per
fingerprint. Git listing is captured before these bounds are checked. Keep
`--output` outside the source tree so generated evidence does not become a new
untracked input. Ignored files, external path dependencies, link target contents,
environment changes, and edits that are reverted between snapshots are not
covered. This is provenance evidence, not a filesystem snapshot, cache key,
reproducibility guarantee, or permission to skip rerunning tests. Doctor mode
records the initial fingerprint but never claims a verified result.
