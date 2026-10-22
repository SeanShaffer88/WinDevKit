# {{REPO}} engineering notes

- Read this file and relevant module contracts before editing. Preserve user changes and public C ABI behavior.
- Keep pure logic testable off Windows. Keep Win32 bindings narrow, documented and explicitly linked to their system libraries.
- Rust/std-only is the default, not a reason to suppress a demonstrably better alternative. When an existing language, dependency, renderer, packaging or architecture choice has a better alternative, explain the concrete benefit, evidence, tradeoffs and migration cost. Recommend whether to revisit it; do not silently change an explicit user constraint.
- A new dependency needs a written justification. Pure Rust, zero third-party dependencies and zero extra runtime requirements are different properties; describe them accurately.
- For shared helpers, prefer a reviewed WinCommon snapshot when enabled. Preserve vendor provenance/hashes; do not overwrite vendor files during ordinary builds.
- Establish baselines before performance changes. Keep optimizations only when measured gains justify complexity and correctness remains intact. Report corpus, machine and limits.
- Every exported fallible FFI body needs a panic/error boundary with documented sentinel returns. Keep panic unwinding enabled for catch_unwind to work; invalid pointers and allocation failure cannot be recovered this way. Free C-owned results only through the producing DLL.
- Run fmt, full workspace clippy/tests with the lockfile, and Windows-target checks. Use WinDevKit's full gate; quick mode is explicitly partial. Native Windows release linking/runtime/C ABI tests are separate requirements.
- Reuse the WinDevKit REA workflow for competitor investigations. Record source revisions, evidence, licensing and limitations. Never report partial inventory as completed semantic or runtime analysis.
- Work in substantial, coherent batches. Verify the final changes, keep documentation accurate and report remaining validation needs without inventing results.
