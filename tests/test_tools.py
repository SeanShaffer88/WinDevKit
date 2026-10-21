"""Offline behavioral checks for the shared tools; no GitHub writes."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

KIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publisher', KIT / 'tools/publish.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class GateTests(unittest.TestCase):
    def gate(self, args=(), target=True, failure='', rustup_fail=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'cargo').write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\ncase "$*" in *"$FAIL_STEP"*) if [ -n "$FAIL_STEP" ]; then exit 17; fi;; esac\n')
            (root / 'rustup').write_text('#!/bin/sh\n' + ('exit 3\n' if rustup_fail else ('echo x86_64-pc-windows-msvc\n' if target else 'echo x86_64-unknown-linux-gnu\n')))
            for file in [root / 'cargo', root / 'rustup']:
                file.chmod(0o755)
            env = dict(os.environ, PATH=tmp + os.pathsep + os.environ['PATH'], CALLS=str(root / 'calls'), FAIL_STEP=failure)
            result = subprocess.run(['bash', str(KIT / 'tools/gate.sh'), *args], env=env, text=True, capture_output=True)
            calls = (root / 'calls').read_text() if (root / 'calls').exists() else ''
            return result, calls

    def test_missing_target_and_rustup_failure_never_pass(self):
        for opts in [dict(target=False), dict(rustup_fail=True)]:
            r, calls = self.gate(**opts)
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn('GREEN', r.stdout)
            self.assertEqual(calls, '')

    def test_quick_is_explicitly_partial(self):
        r, calls = self.gate(['--quick'], target=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('PARTIAL', r.stdout)
        self.assertNotIn('GATE GREEN', r.stdout)
        self.assertNotIn('--target', calls)
        self.assertIn('test --workspace --locked', calls)

    def test_full_gate_enforces_workspace_lockfile_and_windows(self):
        r, calls = self.gate()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(calls.count('--target x86_64-pc-windows-msvc'), 2)
        self.assertIn('GATE GREEN', r.stdout)
        for line in calls.splitlines()[1:]:
            self.assertIn('--workspace', line)
            self.assertIn('--locked', line)

    def test_failure_stops_later_steps(self):
        for step in ['fmt', 'clippy --workspace --all-targets', 'clippy --workspace --target', 'check --workspace', 'test --workspace']:
            r, calls = self.gate(failure=step)
            self.assertEqual(r.returncode, 17)
            self.assertNotIn('GATE GREEN', r.stdout)
            self.assertIn(step, calls)

    def test_unknown_options_fail(self):
        self.assertNotEqual(self.gate(['--quik'])[0].returncode, 0)


class ScaffoldTests(unittest.TestCase):
    def scaffold(self, output, name='HTTPServer', prefix='hs', description='A "quoted" path \\ tool'):
        return subprocess.run([sys.executable, str(KIT / 'tools/scaffold-dll.py'), '--name', name, '--prefix', prefix, '--out', str(output), '--description', description], text=True, capture_output=True)

    def test_output_names_escaping_and_no_leftover_tokens(self):
        import tomllib
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'new'
            r = self.scaffold(out)
            self.assertEqual(r.returncode, 0, r.stderr)
            manifest = tomllib.loads((out / 'Cargo.toml').read_text())
            self.assertEqual(manifest['package']['name'], 'http-server')
            self.assertEqual(manifest['package']['description'], 'A "quoted" path \\ tool')
            self.assertTrue((out / 'include/httpserver.h').is_file())
            self.assertIn('HTTP_SERVER_H', (out / 'include/httpserver.h').read_text())
            self.assertIn('HS_OK', (out / 'src/lib.rs').read_text())
            self.assertEqual(manifest['profile']['release']['panic'], 'unwind')
            for file in out.rglob('*'):
                if file.is_file():
                    self.assertNotIn('{{', file.read_text())
            self.assertNotEqual(self.scaffold(out).returncode, 0)

    def test_bad_inputs_create_nothing(self):
        for name, prefix, desc in [('bad/name', 'x', 'fine'), ('Good', 'bad-prefix', 'fine'), ('Good', 'x', 'bad\nline')]:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / 'new'
                self.assertNotEqual(self.scaffold(out, name, prefix, desc).returncode, 0)
                self.assertFalse(out.exists())


class PublisherTests(unittest.TestCase):
    def test_process_and_structured_errors_fail_even_with_sha_in_message(self):
        for result in [subprocess.CompletedProcess([], 1, 'sha error', 'oops'), subprocess.CompletedProcess([], 0, '{"isError":true,"error":"sha mismatch"}', '')]:
            with patch.object(publisher.subprocess, 'run', return_value=result):
                with self.assertRaises(RuntimeError):
                    publisher.gh_call('tool', {})

    def test_write_error_and_verification_unavailability_exit_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'file.txt').write_text('text')
            args = ['publish.py', '--owner', 'owner', '--repo', 'repo', '--root', tmp, '--message', 'message', 'file.txt']
            for write_error in [True, False]:
                with patch.object(sys, 'argv', args), patch.object(publisher, 'current_sha', return_value='abc'), patch.object(publisher, 'gh_call', return_value=('error sha mismatch', '') if write_error else ('ok', '')), patch.object(publisher, 'raw_bytes', side_effect=OSError('offline')):
                    with self.assertRaises(SystemExit) as err:
                        publisher.main()
                    self.assertEqual(err.exception.code, 1)

    def test_explicit_remote_404_allows_create_but_auth_failure_does_not(self):
        missing = subprocess.CompletedProcess([], 1, '{"status":404,"message":"Not Found"}', '')
        with patch.object(publisher.subprocess, 'run', return_value=missing):
            self.assertIsNone(publisher.current_sha('owner', 'repo', 'file', 'main'))
        denied = subprocess.CompletedProcess([], 1, '{"status":403,"message":"Forbidden"}', '')
        with patch.object(publisher.subprocess, 'run', return_value=denied):
            with self.assertRaises(RuntimeError):
                publisher.current_sha('owner', 'repo', 'file', 'main')

    def test_unrecognized_sha_response_is_not_treated_as_absent(self):
        with patch.object(publisher, 'gh_call', return_value=('unknown response', '')):
            with self.assertRaises(RuntimeError):
                publisher.current_sha('owner', 'repo', 'file', 'main')

    def test_success_requires_exact_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'file.txt').write_text('text')
            args = ['publish.py', '--owner', 'owner', '--repo', 'repo', '--root', tmp, '--message', 'message', 'file.txt']
            with patch.object(sys, 'argv', args), patch.object(publisher, 'current_sha', return_value=None), patch.object(publisher, 'gh_call', return_value=('successfully published error.rs', '')), patch.object(publisher, 'raw_bytes', return_value=b'text'):
                with self.assertRaises(SystemExit) as err:
                    publisher.main()
                self.assertEqual(err.exception.code, 0)


if __name__ == '__main__':
    unittest.main()
