# Disposable filesystem fixtures

Create a fresh, unique test tree with Python 3.10+ (no dependencies):

```sh
python tools/fixtures.py create
python tools/fixtures.py check /path/printed/by/create
python tools/fixtures.py check /path/printed/by/create --expect-missing cleanup/cache.tmp
```

Each session contains `data/` and `manifest.json`. Point reviewed test operations
at **data only**, never its parent or an unrelated folder. The manifest records
relative entry names, directory structure, file lengths, and SHA-256 digests.
The generated application files are inert data, not real installers or programs.
Fixtures include empty files/folders, Unicode and spaced names, identical content,
a cache sample, settings, and documents to preserve. All content is synthetic.

`check` compares the entire bounded tree and returns JSON containing missing,
added, and changed paths. Exit 0 means the observed differences exactly match
all `--expect-missing` entries, with no additions or content/type changes.
Exit 1 means differences did not match; exit 2 means inspection or input failed.
An unchanged tree passes with no expected removals. Repeat `--expect-missing`
for multiple exact entries, including removed directory entries. An expected
removal that did not occur fails. After restoring a backup, check again with
no expected removals to verify original contents and directory structure.

Neither command invokes an application, deletes a tree, touches the registry,
elevates, or creates services. Creation always makes a unique directory beneath
`--parent` (the existing system temp directory by default). Manually remove a
session when finished; there is deliberately no recursive deletion command.

Limits: 1,000 entries, 16 MiB total file reads, 32 directory levels, 1 MiB
manifest. Exceeding limits fails instead of silently omitting content. Observed
symlinks and Windows reparse entries are recorded by type and never followed;
root reparse entries are rejected. Changing a link target is not detected.
Concurrent filesystem replacement can race metadata checks, including through
ancestor links: this is a developer test aid, not adversarial isolation. Use
only quiescent disposable trees and reviewed test code. Use a disposable Windows
VM for destructive application tests; this tool cannot contain an uninstaller.

The comparison checks content and basic entry type, not timestamps, ACLs, alternate
data streams, hard-link identity, or physical allocation. Treat the manifest as
local test evidence, not authenticated proof. The current tool does not seed
registry keys, real installed apps, locked files, VSS state, or Windows recovery
points. Windows native behavior remains unverified; portable tests ran on Linux.

Run regression checks with `python -m unittest discover -s tests -v`.
