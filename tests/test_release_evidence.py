"""Exercise the public CLI with an actual temporary package and tampered evidence."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/release-evidence.py'
EXAMPLE = ROOT / 'examples/release-evidence/fastsearch-v0.1.0-preview.1.json'


class ReleaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = json.loads(EXAMPLE.read_text(encoding='utf-8'))
        self.data = b'synthetic release package\x00\xff'
        (self.root / 'package.zip').write_bytes(self.data)
        self.record['artifacts'] = [dict(path='package.zip', sha256=hashlib.sha256(self.data).hexdigest(),
                                       size=len(self.data), url='https://example.org/package.zip',
                                       architecture='synthetic-test')]

    def run_record(self, record=None, preflight=True, raw=None):
        path = self.root / 'record.json'
        path.write_text(raw if raw is not None else json.dumps(record or self.record), encoding='utf-8')
        args = [sys.executable, str(TOOL), str(path), '--artifacts-dir', str(self.root)]
        if preflight:
            args.append('--release-preflight')
        return subprocess.run(args, capture_output=True, text=True, check=False)

    def test_real_bytes_and_public_example(self):
        result = self.run_record()
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(TOOL), str(EXAMPLE)], capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_tamper_and_size_mismatch_are_failures(self):
        (self.root / 'package.zip').write_bytes(b'x' * len(self.data))
        self.assertNotEqual(self.run_record().returncode, 0)
        (self.root / 'package.zip').write_bytes(self.data)
        self.record['artifacts'][0]['size'] += 1
        self.assertNotEqual(self.run_record().returncode, 0)

    def test_missing_or_escape_artifacts_are_failures(self):
        for name in ['missing.zip', '../outside.zip', '/package.zip', 'C:/package.zip',
                     'package.zip:stream', 'dir/../package.zip', 'dir\\package.zip']:
            with self.subTest(name=name):
                self.record['artifacts'][0]['path'] = name
                self.assertNotEqual(self.run_record().returncode, 0)

    def test_symlink_artifact_is_refused(self):
        link = self.root / 'alias.zip'
        try:
            link.symlink_to(self.root / 'package.zip')
        except OSError:
            self.skipTest('host lacks unprivileged symlinks')
        self.record['artifacts'][0]['path'] = 'alias.zip'
        self.assertNotEqual(self.run_record().returncode, 0)

    @unittest.skipUnless(os.name == 'nt', 'Windows junction behavior')
    def test_windows_junction_to_inside_directory_is_refused(self):
        actual = self.root / 'actual'
        actual.mkdir()
        (actual / 'package.zip').write_bytes(self.data)
        link = self.root / 'linked'
        result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(actual)],
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            self.record['artifacts'][0]['path'] = 'linked/package.zip'
            self.assertNotEqual(self.run_record().returncode, 0)
            self.assertEqual((actual / 'package.zip').read_bytes(), self.data)
        finally:
            link.rmdir()

    def test_partial_or_failed_evidence_is_preserved_but_cannot_pass_preflight(self):
        for status in ['failed', 'not_run']:
            record = copy.deepcopy(self.record)
            record['checks'][0]['status'] = status
            self.assertEqual(self.run_record(record, preflight=False).returncode, 0)
            self.assertNotEqual(self.run_record(record).returncode, 0)
        self.record['source']['tree_state'] = 'dirty'
        self.assertNotEqual(self.run_record().returncode, 0)

    def test_stable_cannot_hide_partial_machine_acceptance(self):
        self.record['release']['maturity'] = 'stable'
        self.assertNotEqual(self.run_record().returncode, 0)

    def test_missing_unknown_duplicate_and_invalid_fields(self):
        variants = []
        for key, value in [('schema_version', True), ('recorded_on', '2026-02-30'), ('unknown', 'typo')]:
            record = copy.deepcopy(self.record); record[key] = value; variants.append(record)
        record = copy.deepcopy(self.record); del record['notices']; variants.append(record)
        record = copy.deepcopy(self.record); record['checks'].append(record['checks'][0]); variants.append(record)
        record = copy.deepcopy(self.record); record['source']['commit'] = 'main'; variants.append(record)
        record = copy.deepcopy(self.record); record['artifacts'][0]['sha256'] = '123'; variants.append(record)
        for record in variants:
            with self.subTest(record=record):
                self.assertNotEqual(self.run_record(record).returncode, 0)
        self.assertNotEqual(self.run_record(raw='{"schema_version":1,"schema_version":1}').returncode, 0)


if __name__ == '__main__':
    unittest.main()
