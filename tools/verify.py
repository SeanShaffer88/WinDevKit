#!/usr/bin/env python3
"""Portable Rust verification with durable evidence. Python 3.10+, stdlib only."""
import argparse
import hashlib
import stat
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import time


def execute(command, cwd, log, timeout):
    """No shell interpolation; keep compiler output out of the JSON summary."""
    started = time.monotonic()
    with log.open('w', encoding='utf-8') as stream:
        try:
            result = subprocess.run(command, cwd=cwd, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout, check=False)
            status = 'passed' if result.returncode == 0 else 'failed'
            code = result.returncode
        except subprocess.TimeoutExpired:
            status, code = 'timed_out', None
        except OSError as error:
            stream.write(str(error))
            status, code = 'unavailable', None
    return dict(command=command, status=status, exit_code=code,
                seconds=round(time.monotonic() - started, 3), log=str(log))


def plan(targets, allow_warnings=False, offline=False):
    flags = ['--locked'] + (['--offline'] if offline else [])
    lint = [] if allow_warnings else ['--', '-D', 'warnings']
    steps = [('format', ['cargo', 'fmt', '--all', '--', '--check']),
             ('host-lint', ['cargo', 'clippy', '--all-targets', *flags, *lint]),
             ('tests', ['cargo', 'test', '--all-targets', *flags]),
             ('doctests', ['cargo', 'test', '--doc', *flags]),
             ('host-build', ['cargo', 'build', *flags])]
    for target in targets:
        steps.extend([
            (f'{target}-lint', ['cargo', 'clippy', '--all-targets', '--target', target, *flags, *lint]),
            (f'{target}-check', ['cargo', 'check', '--all-targets', '--target', target, *flags])])
    return steps


def overall(steps):
    if any(s['status'] in ('failed', 'timed_out', 'unavailable') for s in steps):
        return 'failed'
    return 'passed_with_limits' if any(s['status'] == 'skipped' for s in steps) else 'passed'


def probe(command, root):
    try:
        r = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=15)
        return dict(exit_code=r.returncode, text=(r.stdout + r.stderr).strip()[:4000])
    except (OSError, subprocess.TimeoutExpired) as error:
        return dict(exit_code=None, text=str(error))


def source_state(root):
    """Fingerprint Git-listed worktree bytes without reading link targets."""
    try:
        result = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                                cwd=root, capture_output=True, timeout=15, check=True)
        names = sorted(set(result.stdout.split(b'\0')) - {b''})
        if len(names) > 100000 or len(result.stdout) > 16 * 1024 * 1024:
            raise ValueError('Source inventory limit exceeded')
        digest = hashlib.sha256()
        total = 0
        for name in names:
            path = root / os.fsdecode(name)
            digest.update(len(name).to_bytes(8, 'big'))
            digest.update(name)
            try:
                meta = path.lstat()
            except FileNotFoundError:
                digest.update(b'missing')
                continue
            if stat.S_ISLNK(meta.st_mode):
                content = os.fsencode(os.readlink(path))
                digest.update(b'link')
            elif stat.S_ISREG(meta.st_mode):
                if getattr(meta, 'st_file_attributes', 0) & 0x400:
                    raise ValueError('Reparse entry prevents source fingerprinting')
                with path.open('rb') as stream:
                    content = stream.read(128 * 1024 * 1024 - total + 1)
                digest.update(b'file')
            else:
                raise ValueError('Submodule, directory, or special source entry not fingerprinted')
            total += len(content)
            if total > 128 * 1024 * 1024:
                raise ValueError('Source byte limit exceeded')
            digest.update((meta.st_mode & 0o111).to_bytes(2, 'big'))
            digest.update(len(content).to_bytes(8, 'big'))
            digest.update(content)
        head = probe(['git', 'rev-parse', '--verify', 'HEAD'], root)
        return dict(status='available', sha256=digest.hexdigest(), files=len(names),
                    bytes=total, revision=head['text'] if head['exit_code'] == 0 else None)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return dict(status='unavailable', reason=str(error))


def source_check(before, after):
    if before['status'] != 'available' or after['status'] != 'available':
        return dict(name='source-stability', status='skipped',
                    reason='Source fingerprint unavailable; results cannot establish unchanged inputs')
    stable = before == after
    return dict(name='source-stability', status='passed' if stable else 'failed',
                reason='Git-listed inputs unchanged' if stable else 'Inputs changed during verification; rerun checks')


def save_report(out, report):
    # Staged replacement preserves the preceding checkpoint if writing fails.
    staged = out / 'report.json.tmp'
    try:
        with staged.open('w', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staged, out / 'report.json')
    finally:
        staged.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--output', type=Path, help='Parent for a new unique evidence directory')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--allow-warnings', action='store_true', help='Record existing warnings without denying them')
    parser.add_argument('--timeout', type=float, default=900, help='Seconds per command')
    parser.add_argument('--target', action='append', default=[], help='Additional installed Windows target')
    parser.add_argument('--doctor', action='store_true', help='Inspect only; do not run Cargo/build scripts')
    args = parser.parse_args(argv)
    root = args.project.resolve()
    if not (root / 'Cargo.toml').is_file():
        parser.error('project must contain Cargo.toml')
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('timeout must be positive')
    parent = args.output.resolve() if args.output else Path(tempfile.gettempdir()) / 'windevkit-evidence'
    parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='verify-', dir=parent))
    report = dict(schema_version=1, project=str(root), host=platform.platform(),
                  warning_policy='allow' if args.allow_warnings else 'deny',
                  offline=args.offline, doctor=args.doctor, status='in_progress', steps=[])
    for name, command in [('git', ['git', 'status', '--short', '--branch']),
                          ('rustc', ['rustc', '-Vv']), ('cargo', ['cargo', '-V']),
                          ('targets', ['rustup', 'target', 'list', '--installed'])]:
        report[name] = probe(command, root)
    report['limits'] = ['Host tests do not verify Windows UI, accessibility, or recovery.',
                        'Cross-target checks do not link or execute Windows binaries.',
                        'Timeout kills the direct command; descendant build tools may survive.']
    if report['git']['exit_code'] != 0:
        report['limits'].append('Git state unavailable; do not assume a clean or publishable checkout.')
    installed = report['targets']['text'].splitlines() if report['targets']['exit_code'] == 0 else []
    targets = list(dict.fromkeys(args.target or [t for t in installed if 'windows' in t]))
    report['source_before'] = source_state(root)
    save_report(out, report)
    if not args.doctor:
        missing = [t for t in targets if t not in installed]
        for name, command in plan([t for t in targets if t in installed], args.allow_warnings, args.offline):
            print(f'Running {name}', flush=True)
            result = execute(command, root, out / f'{name}.log', args.timeout)
            report['steps'].append(dict(name=name, **result))
            # Persist after each step, so interrupted batches retain completed evidence.
            save_report(out, report)
        for target in missing:
            report['steps'].append(dict(name=target, status='unavailable', reason='Target not installed'))
        if not targets:
            report['steps'].append(dict(name='windows-checks', status='skipped', reason='No Windows targets installed'))
        if os.name != 'nt':
            report['steps'].append(dict(name='windows-native-build', status='skipped', reason='Requires Windows runner'))
        report['source_after'] = source_state(root)
        report['steps'].append(source_check(report['source_before'], report['source_after']))
        report['status'] = overall(report['steps'])
    else:
        report['status'] = 'inspection_only'
    save_report(out, report)
    print(f"{report['status']}: {out / 'report.json'}")
    return 1 if report['status'] == 'failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
