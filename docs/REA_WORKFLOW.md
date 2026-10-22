# Evidence-led competitor review with REA

Use REA to investigate a concrete workflow or feature in a local target artifact.
An inventory, static relationship and observed runtime behavior are different
kinds of evidence. Keep the artifact revision/digest and limitations beside the
feature decision. REA is a research tool; it is not a runtime dependency of the
Windows applications built with this kit.

Official sources: [REA](https://github.com/morluto/rea), its
[CLI guide](https://github.com/morluto/rea/blob/main/docs/cli.md) and
[JavaScript guide](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md).
This batch used npm package `rea-agents@6.7.0`, invoked directly; it did not
rewrite agent configuration or register global tools.

## Repeatable static JavaScript review

1. Obtain the official target source/artifact and record its revision and license.
2. Run REA doctor/capabilities on the actual analysis host. Linux JavaScript
   analysis requires a working procps-compatible `ps` in REA's child environment.
3. Select relevant sources explicitly so the time/heap budget stays useful.
4. Save JSON, summarize it and inspect limitations before interpreting results.
5. Cross-check source-backed behavior and run the target if runtime proof is
   needed. Assess each feature for the receiving app's architecture and users.
6. Implement original code, benchmark/test it and document what remains unknown.

Example (replace the source path with one actually present in the target):

```sh
npx --yes rea-agents@6.7.0 analyze-javascript-application ./target-app \
  --source-path src/search.js --format json > rea-report.json
python WinDevKit/tools/rea-summary.py rea-report.json --out rea-summary.json
```

The summary helper exits 1 for a blocked/partial result and 2 for an unknown or
malformed envelope. A recognized evidence envelope exits 0, but its static
limits and unselected-source count remain in the summary. Exit 0 never means
a competitor feature was proven to work at runtime.

Do not bypass ownership checks or invent the relationship graph when a provider
is unavailable. Use a supported host to complete that part of the investigation.
Native binaries require a compatible analysis provider; a JS source review is
not a substitute for native-binary analysis.

See [the first comparison](research/SEARCH_COMPARISON.md) for the concrete
findings, per-feature decisions and this environment's REA limitation.
