#!/usr/bin/env python3
"""Create disposable filesystem fixtures and compare their contents. Stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import tempfile

LIMIT = 16 * 1024 * 1024
ENTRY_LIMIT = 1000


def is_link(meta):
    return stat.S_ISLNK(meta.st_mode) or bool(getattr(meta, 'st_file_attributes', 0) & 0x400)


def inventory(root):
    if is_link(root.lstat()) or not root.is_dir():
        raise ValueError('Fixture data root must be a real directory')
    entries, pending, total = {}, [(root, 0)], 0
    while pending:
        folder, depth = pending.pop()
        if depth > 32:
            raise ValueError('Fixture depth limit exceeded')
        for path in sorted(folder.iterdir()):
            if len(entries) >= ENTRY_LIMIT:
                raise ValueError('Fixture entry limit exceeded')
            key = path.relative_to(root).as_posix()
            meta = path.lstat()
            if is_link(meta):
                entries[key] = {'kind': 'link'}  # Never traverse or read targets.
            elif stat.S_ISDIR(meta.st_mode):
                entries[key] = {'kind': 'directory'}
                pending.append((path, depth + 1))
            elif stat.S_ISREG(meta.st_mode):
                # Bound reads even when a file grows after metadata inspection.
                with path.open('rb') as stream:
                    content = stream.read(LIMIT - total + 1)
                total += len(content)
                if total > LIMIT:
                    raise ValueError('Fixture content limit exceeded')
                entries[key] = {'kind': 'file', 'bytes': len(content),
                                'sha256': hashlib.sha256(content).hexdigest()}
            else:
                raise ValueError(f'Unsupported fixture entry: {key}')
    return entries


def create(parent):
    session = Path(tempfile.mkdtemp(prefix='windevkit-fixture-', dir=parent))
    data = session / 'data'
    data.mkdir()
    files = {'keep/documents/important.txt': b'Keep this document.\n',
             'keep/Unicode café 雪.txt': b'Unicode path fixture.\n',
             'cleanup/cache.tmp': b'x' * 4096,
             'cleanup/empty.tmp': b'',
             'duplicates/first.bin': b'duplicate content\n',
             'duplicates/second.bin': b'duplicate content\n',
             'application/settings.json': b'{"theme":"dark"}\n',
             'application/program.dat': b'Inert sample; not an executable.\n'}
    for name, content in files.items():
        path = data / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    (data / 'empty folder').mkdir()
    manifest = {'schema_version': 1, 'entries': inventory(data)}
    with (session / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2, ensure_ascii=False)
    return session


def valid_key(key):
    return (isinstance(key, str) and bool(key) and '\\' not in key and ':' not in key
            and not key.startswith('/') and all(p not in ('', '.', '..') for p in key.split('/')))


def compare(session, expected_missing=()):
    manifest_path = session / 'manifest.json'
    if is_link(manifest_path.lstat()):
        raise ValueError('Manifest must not be a link or reparse entry')
    with manifest_path.open('rb') as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError('Manifest exceeds size limit')
    manifest = json.loads(raw)
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        raise ValueError('Unsupported manifest schema')
    before = manifest.get('entries')
    if not isinstance(before, dict) or len(before) > ENTRY_LIMIT or not all(valid_key(k) for k in before):
        raise ValueError('Invalid manifest entries')
    expected = set(expected_missing)
    if not all(valid_key(k) and k in before for k in expected):
        raise ValueError('Expected removals must name exact entries from the manifest')
    after = inventory(session / 'data')
    missing = sorted(before.keys() - after.keys())
    added = sorted(after.keys() - before.keys())
    changed = sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
    return {'schema_version': 1, 'passed': set(missing) == expected and not added and not changed,
            'missing': missing, 'added': added, 'changed': changed,
            'expected_missing': sorted(expected)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    seed = sub.add_parser('create')
    seed.add_argument('--parent', type=Path, default=Path(tempfile.gettempdir()))
    check = sub.add_parser('check')
    check.add_argument('session', type=Path)
    check.add_argument('--expect-missing', action='append', default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == 'create':
            print(create(args.parent))
            return 0
        report = compare(args.session, args.expect_missing)
        print(json.dumps(report, indent=2))
        return 0 if report['passed'] else 1
    except (OSError, ValueError) as error:
        print(json.dumps({'passed': False, 'error': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
