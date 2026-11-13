# VM verification pack

Reusable clean-machine verification for Windows releases — the
check that answers "does it actually run on a machine that has
nothing of ours on it?" (PAIN_POINTS #54; the kit collection's
standing gap was that releases were hash- and import-verified
from a Linux VM, while the load-and-run check waited on ad-hoc
manual sessions.)

## The protocol

1. **Start from a clean snapshot.** A Windows VM (or a spare
   machine) with nothing installed beyond Windows itself and
   PowerShell. Snapshot it *before* the run; revert afterwards.
   One snapshot per release under test — never verify two
   releases against the same un-reverted machine and call both
   "clean".
2. **Download like a user.** Fetch the release zips and their
   `SHA256SUMS.txt` from the Releases page, into one folder.
   Don't copy binaries over from a build machine — the point is
   meeting the files exactly as a user gets them.
3. **Run the verifier.**

   ```powershell
   ./Verify-Release.ps1 C:\Downloads\SomeKit-release
   ```

   It checks each zip's SHA-256 against `SHA256SUMS.txt`,
   extracts to a fresh folder, parses every DLL/EXE's imports
   (flagging anything that isn't a Windows system library — the
   "works on my machine, missing DLL on yours" failure), then
   **loads each DLL and calls its `<prefix>_version` export**,
   recording the string it answers with.
4. **File the report.** `verify-report.json` (machine, OS, per-
   file results, verdict) is the evidence. Attach it to the
   release notes or the issue that asked for the check; a claim
   of "field-verified" should point at one of these.

Exit codes: `0` every check passed, `1` a check failed,
`2` usage error. Off Windows, the hash/import checks still run
(the PE parser is pure PowerShell) and the load test reports
**Skipped** — never Passed. A skipped load test is not a
verified binary.

## The pieces

- `Verify-Release.ps1` — the protocol runner above.
- `Get-PeInfo.ps1` — a dependency-free PE header reader
  (imports + exports + machine type). Safe on untrusted files:
  it parses headers only, never loads or executes the binary.

## Honest limits

- The load test proves a DLL loads and its version handshake
  answers. It does not exercise the kit's real features — pair
  it with the kit's own examples (`examples/<kit>-python/`) on
  the same clean machine for that.
- The system-DLL list encodes the collection's release rule
  (system libraries + `api-ms-`/`ext-ms-` API sets). A binary
  that legitimately ships its own runtime DLL next to itself
  will be flagged; that's deliberate — the reviewer decides,
  with the flag in front of them.
