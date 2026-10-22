"""Compile generated projects, including the optional vendored shared crate."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('cargo'), 'Rust toolchain required')
class GeneratedProjectTests(unittest.TestCase):
    def test_generated_standalone_project_passes_rust_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'project'
            subprocess.run([sys.executable, str(KIT / 'tools/scaffold-dll.py'), '--name', 'IntegrationKit', '--prefix', 'ik', '--out', str(out)], check=True, capture_output=True)
            for args in [['fmt', '--all'], ['generate-lockfile', '--offline'], ['clippy', '--all-targets', '--locked', '--', '-D', 'warnings'], ['test', '--locked'], ['test', '--release', '--locked']]:
                result = subprocess.run(['cargo', *args], cwd=out, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_optional_vendoring_preserves_hashes_and_uses_common(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'common'
            (source / 'src').mkdir(parents=True)
            (source / 'Cargo.toml').write_text('[package]\nname="win-common"\nversion="0.1.0"\nedition="2021"\n[dependencies]\n')
            (source / 'src/lib.rs').write_text('// input fixture; real shared crate checked separately\n')
            (source / 'LICENSE').write_text('MIT\n')
            (source / 'README.md').write_text('fixture\n')
            out = root / 'project'
            result = subprocess.run([sys.executable, str(KIT / 'tools/scaffold-dll.py'), '--name', 'SharedKit', '--prefix', 'sk', '--out', str(out), '--with-win-common', str(source)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            vendor = out / 'vendor/win-common'
            inventory = json.loads((vendor / 'VENDORED.json').read_text())
            for name, digest in inventory['files_sha256'].items():
                self.assertEqual(hashlib.sha256((vendor / name).read_bytes()).hexdigest(), digest)
            self.assertIn('win-common = { path = "vendor/win-common" }', (out / 'Cargo.toml').read_text())
            self.assertIn('win_common::json::escape', (out / 'src/lib.rs').read_text())
            self.assertIn('win_common::ffi::free_c_string', (out / 'src/ffi.rs').read_text())
