# On-Machine Verification Checklist

Our recurring gap: features compile, CI passes, and the first *real*
Windows run happens weeks later (SafeReturn's VSS runtime, WinRecovery's
live enumeration, InstallScope's SR/DPI behavior were all in this state).
Run this checklist on a real Windows machine (or VM) before any release
claim, and record results in the project's README verification section —
with Windows edition/build, elevation, and date. "CI green" is never a
substitute for a line in this table.

## Setup
- [ ] Windows edition + build recorded (winver), machine/VM specs noted
- [ ] Fresh user account AND the normal daily account, if the app is per-user
- [ ] Run once NOT elevated, once elevated — record which features gate on it
- [ ] Display scaling at 100% and 150%+; second monitor if available
- [ ] High contrast theme on for one pass; keyboard-only for one pass

## Core workflows
- [ ] Every headline feature exercised end-to-end against REAL data
      (real restore points, real recycle bin, real driver store…)
- [ ] Destructive paths tested only on disposable data/VM snapshots
- [ ] Failure matrix: disk nearly full · target locked/in use · permission
      denied · network location unavailable · required service stopped
- [ ] Cancel/interrupt a long operation mid-flight; state afterwards is sane
- [ ] Kill the process mid-operation; restart; no corruption, no orphans
      (check for leaked shadow copies / temp files / handles)
- [ ] Long paths (>260), Unicode names, spaces in paths

## Data & recovery
- [ ] Settings/data survive upgrade and uninstall as documented
- [ ] Backup/undo path actually restores (not just "says it did")
- [ ] Corrupt/truncated data file → clear error, no crash, no silent default

## Report
- [ ] README verification section updated: what ran, where, result, date
- [ ] Anything not run is listed as NOT VERIFIED — explicitly, by name
