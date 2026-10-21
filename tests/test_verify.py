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
