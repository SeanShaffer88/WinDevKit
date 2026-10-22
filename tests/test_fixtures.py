import importlib.util
from pathlib import Path
import json
import os
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('fixtures', Path(__file__).resolve().parents[1] / 'tools/fixtures.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name)
        self.session = f.create(self.parent)

    def test_pristine_tree_and_unique_sessions(self):
        self.assertTrue(f.compare(self.session)['passed'])
        second = f.create(self.parent)
        self.assertNotEqual(second, self.session)
        self.assertTrue(f.compare(second)['passed'])

    def test_exact_expected_removal_and_restoration(self):
        path = self.session / 'data/cleanup/cache.tmp'
        content = path.read_bytes()
        path.unlink()
        self.assertFalse(f.compare(self.session)['passed'])
        self.assertTrue(f.compare(self.session, ['cleanup/cache.tmp'])['passed'])
        path.write_bytes(content)
        self.assertTrue(f.compare(self.session)['passed'])
        self.assertFalse(f.compare(self.session, ['cleanup/cache.tmp'])['passed'])

    def test_same_size_edits_and_unexpected_additions(self):
        path = self.session / 'data/application/program.dat'
        path.write_bytes(b'!' * path.stat().st_size)
        (self.session / 'data/new.txt').write_bytes(b'new')
        report = f.compare(self.session)
        self.assertFalse(report['passed'])
        self.assertEqual(report['changed'], ['application/program.dat'])
        self.assertEqual(report['added'], ['new.txt'])

    def test_corrupt_future_and_traversal_manifests_fail(self):
        path = self.session / 'manifest.json'
        for value in ['garbage', '{"schema_version":2}',
                      '{"schema_version":1,"entries":{"../outside":{}}}']:
            path.write_text(value)
            with self.assertRaises(ValueError):
                f.compare(self.session)

    def test_unlisted_expected_removal_fails(self):
        for name in ['../outside', '/absolute', 'C:escape', 'not-listed']:
            with self.assertRaises(ValueError):
                f.compare(self.session, [name])

    def test_read_budget_fails_instead_of_truncating(self):
        from unittest.mock import patch
        with patch.object(f, 'LIMIT', 8):
            with self.assertRaisesRegex(ValueError, 'content limit'):
                f.compare(self.session)

    @unittest.skipIf(os.name == 'nt', 'Symlink privilege unavailable on some Windows runners')
    def test_links_never_read_outside_data(self):
        outside = self.parent / 'outside'
        outside.mkdir()
        (outside / 'secret').write_bytes(b'private')
        (self.session / 'data/link').symlink_to(outside, target_is_directory=True)
        entries = f.inventory(self.session / 'data')
        self.assertEqual(entries['link'], {'kind': 'link'})
        self.assertNotIn('link/secret', entries)
        self.assertEqual((outside / 'secret').read_bytes(), b'private')

    @unittest.skipIf(os.name == 'nt', 'Requires symlink support')
    def test_replaced_data_root_is_rejected(self):
        import shutil
        shutil.rmtree(self.session / 'data')
        (self.session / 'data').symlink_to(self.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            f.compare(self.session)


if __name__ == '__main__':
    unittest.main()
