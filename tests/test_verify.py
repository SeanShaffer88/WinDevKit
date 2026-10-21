import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('verify', Path(__file__).resolve().parents[1] / 'tools/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerifyTests(unittest.TestCase):
    def test_plan_keeps_full_tests_doc_build_and_locked_dependencies(self):
        commands = dict(v.plan(['x86_64-pc-windows-msvc'], offline=True))
        self.assertIn('--all-targets', commands['tests'])
        self.assertIn('--doc', commands['doctests'])
        self.assertIn('host-build', commands)
        for name, command in commands.items():
            if name != 'format':
                self.assertIn('--locked', command)
                self.assertIn('--offline', command)
        self.assertIn('warnings', commands['host-lint'])
        self.assertNotIn('warnings', dict(v.plan([], allow_warnings=True))['host-lint'])

    def test_quick_profile_keeps_host_feedback_and_omits_full_gate_steps(self):
        commands = dict(v.plan(['x86_64-pc-windows-msvc'], profile='quick'))
        self.assertEqual(set(commands), {'format', 'host-lint', 'tests'})
        self.assertIn('--all-targets', commands['tests'])
        self.assertNotIn('doctests', commands)
        self.assertNotIn('host-build', commands)
        self.assertNotIn('x86_64-pc-windows-msvc-check', commands)

    def test_quick_profile_is_reported_as_partial_coverage(self):
        from unittest.mock import patch
        import json
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'project'
            root.mkdir()
            (root / 'Cargo.toml').write_text('[package]')
            source = dict(status='available', sha256='stable', revision='abc')
            result = dict(status='passed', exit_code=0, seconds=0.0, log='unused')
            with (patch.object(v, 'probe', return_value=dict(exit_code=0, text='')),
                  patch.object(v, 'source_state', return_value=source),
                  patch.object(v, 'execute', return_value=result)):
                code = v.main([str(root), '--profile', 'quick', '--output', str(Path(folder) / 'evidence')])
            report = json.loads(next((Path(folder) / 'evidence').glob('*/report.json')).read_text())
            self.assertEqual(code, 0)
            self.assertEqual(report['status'], 'passed_with_limits')
            self.assertEqual(report['profile'], 'quick')
            self.assertFalse(report['coverage']['full_profile'])
            self.assertEqual(report['coverage']['included_steps'], ['format', 'host-lint', 'tests'])
            self.assertEqual(report['coverage']['excluded_steps'], ['doctests', 'host-build'])
            skipped = {step['name'] for step in report['steps'] if step['status'] == 'skipped'}
            self.assertTrue({'doctests', 'host-build'} <= skipped)

    def test_failures_timeouts_and_unavailable_commands_are_not_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cases = [([sys.executable, '-c', 'print("compiler error"); raise SystemExit(3)'], 5, 'failed'),
                     ([sys.executable, '-c', 'import time; time.sleep(3)'], .05, 'timed_out'),
                     ([str(root / 'missing-command')], 5, 'unavailable'),
                     ([sys.executable, '-c', 'print("ok")'], 5, 'passed')]
            for i, (cmd, timeout, expected) in enumerate(cases):
                result = v.execute(cmd, root, root / f'{i}.log', timeout)
                self.assertEqual(result['status'], expected)
                self.assertTrue(Path(result['log']).exists())

    def test_skips_are_explicit_and_failure_dominates(self):
        self.assertEqual(v.overall([dict(status='passed'), dict(status='skipped')]), 'passed_with_limits')
        self.assertEqual(v.overall([dict(status='skipped'), dict(status='failed')]), 'failed')
        self.assertEqual(v.overall([dict(status='passed')]), 'passed')

    def test_failed_checkpoint_preserves_previous_report(self):
        from unittest.mock import patch
        import json
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            v.save_report(root, {'status': 'in_progress'})
            with patch.object(v.os, 'replace', side_effect=OSError('disk error')):
                with self.assertRaises(OSError):
                    v.save_report(root, {'status': 'passed'})
            self.assertEqual(json.loads((root / 'report.json').read_text())['status'], 'in_progress')
            self.assertFalse((root / 'report.json.tmp').exists())

    def test_fingerprint_detects_edits_additions_and_deletions(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            path = root / 'input.rs'
            path.write_text('before')
            first = v.source_state(root)
            self.assertEqual(first['status'], 'available')
            self.assertEqual(v.source_check(first, v.source_state(root))['status'], 'passed')
            path.write_text('after!')  # Same size, different bytes.
            self.assertEqual(v.source_check(first, v.source_state(root))['status'], 'failed')
            path.write_text('before')
            extra = root / 'new.rs'
            extra.write_text('new')
            self.assertEqual(v.source_check(first, v.source_state(root))['status'], 'failed')
            extra.unlink()
            self.assertEqual(first, v.source_state(root))
            subprocess.run(['git', 'add', 'input.rs'], cwd=root, check=True)
            tracked = v.source_state(root)
            path.unlink()
            self.assertEqual(v.source_check(tracked, v.source_state(root))['status'], 'failed')

    def test_source_change_during_successful_checks_fails_batch(self):
        import subprocess
        from unittest.mock import patch
        import json
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'project'
            root.mkdir()
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            source = root / 'Cargo.toml'
            source.write_text('[package]')
            def changed(command, cwd, log, timeout):
                source.write_text('[package] # edited during checks')
                return dict(status='passed', exit_code=0, command=command, seconds=0, log=str(log))
            with patch.object(v, 'plan', return_value=[('fake', ['fake'])]), patch.object(v, 'execute', side_effect=changed):
                code = v.main([str(root), '--output', str(Path(folder) / 'evidence')])
            self.assertEqual(code, 1)
            report = json.loads(next((Path(folder) / 'evidence').glob('*/report.json')).read_text())
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['steps'][-1]['name'], 'source-stability')
            self.assertEqual(report['steps'][-1]['status'], 'failed')

    def test_missing_fingerprint_is_never_a_pass(self):
        missing = dict(status='unavailable', reason='broken Git')
        self.assertEqual(v.source_check(missing, missing)['status'], 'skipped')
        self.assertEqual(v.overall([v.source_check(missing, missing)]), 'passed_with_limits')

    def test_doctor_records_broken_git_without_running_cargo(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'Cargo.toml').write_text('[package]\nname="probe"\nversion="0.1.0"\n')
            (root / '.git').write_text('gitdir: /nonexistent/windevkit-test\n')
            self.assertEqual(v.main([str(root), '--doctor', '--output', str(root / 'out')]), 0)
            import json
            report = json.loads(next((root / 'out').glob('*/report.json')).read_text())
            self.assertEqual(report['status'], 'inspection_only')
            self.assertEqual(report['steps'], [])
            self.assertNotEqual(report['git']['exit_code'], 0)
            self.assertTrue(any('Git state unavailable' in limit for limit in report['limits']))


if __name__ == '__main__':
    unittest.main()
