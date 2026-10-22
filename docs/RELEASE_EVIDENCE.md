# Portfolio release evidence v1

Incident 21: the FastSearch release pilot and recovery-tool validation used
different receipts; successful builds, machine checks, published bytes and
remaining hardware gaps had to be reconstructed across reports.

Use [the versioned schema](../schemas/release-evidence-v1.schema.json) and
[FastSearch's completed pilot record](../examples/release-evidence/fastsearch-v0.1.0-preview.1.json).
The schema declares JSON Schema 2020-12. The dependency-free CLI checks the
small keyword subset actually used by this schema plus portfolio rules; it is
not an implementation of the entire JSON Schema dialect.

```powershell
python tools/release-evidence.py examples/release-evidence/fastsearch-v0.1.0-preview.1.json
python tools/release-evidence.py path/to/evidence.json --artifacts-dir path/to/downloads --release-preflight
```

The first command validates structure only. The second also streams SHA-256
and checks byte counts for every listed local asset. It refuses missing files,
links/junctions, path traversal, mismatched bytes, duplicate identities, unknown
fields and duplicate JSON keys. It performs no network requests, execution,
extraction, tagging, uploading or signing. Artifact directories must remain
under the operator's control during verification; this is not an adversarial
filesystem sandbox.

## Record the actual milestone

- `source`: repository URL, exact 40-character Git commit and observed working
  tree state. The record can be committed later than the source it describes.
- `release`: explicit development/prerelease/stable maturity, tag/URL and signing
  status with its actual verification scope. A hash is not publisher authentication.
- `checks`: stable IDs, passed/failed/not_run, kind, platform, operation/results
  and evidence URL. Preserve failed and unrun checks rather than deleting them.
- `real_machine`: passed/partial/not_run, OS/build/CPU, actual operations and
  evidence. Use partial for a developer-host smoke run with clean-host or
  required hardware acceptance outstanding. Compilation alone is not runtime proof.
- `artifacts`: normalized relative filename, exact bytes/SHA-256, download URL
  and architecture. Only list assets that exist for this milestone.
- `notices`: project and bundled/external component notices, canonical URLs and
  redistribution scope. A reference alone does not verify permission or ensure
  the notice was included; inspect the actual package.
- `limitations`: nonempty, specific unresolved checks, compatibility, safety and
  coverage boundaries. Do not include secrets, private host paths or raw logs
  until reviewed for disclosure.

`--release-preflight` additionally requires local bytes, recorded clean source,
all listed checks passed and, for stable maturity, recorded full machine
acceptance. Prereleases can retain partial machine coverage if limits explain
it. This mechanical gate cannot establish that a test ran, that a tag resolves
to the stated commit, that a URL still serves the checked bytes, that a signature
is valid, or that the checklist is sufficient for a particular application.
Those remain explicit reviewer checks. `--release-preflight` is not permission
to distribute restricted upstream material.

## Adoption and existing tools

1. Keep existing gates and per-project runtime/recovery checklists. Add a record
   for an actual completed milestone, then link it from the repository's release
   documentation. Never fill unknown fields with a guessed pass or digest.
2. Review exact-commit CI, actual machine evidence, license/package contents,
   tag resolution and checksums. Re-download published assets for byte checks.
3. Commit the record in the consumer repository. Pin the reviewed WinDevKit
   revision when invoking the verifier from another project; it is a development
   tool, not a runtime dependency.
4. Rerun checks for new source/package bytes; preserve previous records and
   their dates. Do not relabel an old binary as rebuilt because documentation changed.

FastSearch is the first consumer. Its v0.1.0-preview.1 record captures the
already-published exact source and unsigned x64 package, with developer-host
smokes and clean-host/ARM64/x86 gaps. This format adoption does not rebuild,
replace or retag that release. WinDevKit retains an identical example for tests.
Other repositories can adopt it at their next real milestone; no universal
retroactive validation is claimed.

[BuildTrail](https://github.com/SeanShaffer88/BuildTrail) captures local commands,
tool probes, logs, output hashes and AppTrail checkpoints. Keep its original
run format and private evidence store. This portfolio record summarizes a
reviewed release; it does not rewrite BuildTrail/AppTrail storage or turn build
exit-code success into runtime acceptance. Review exports before sharing.

No recurring automation or signing service is configured by this workflow.
