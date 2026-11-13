"""Tests for tools/catalog.py — the catalog generator/checker.

The catalog once promised downloads from standalone kit repositories
that no longer existed (docs/PAIN_POINTS.md #50). These tests pin the
guard: the real tree must check clean, and a kit that appears under
kits/ without a catalog entry (or the reverse) must be caught.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "catalog", ROOT / "tools" / "catalog.py"
)
catalog = importlib.util.module_from_spec(spec)
sys.modules["catalog"] = catalog
spec.loader.exec_module(catalog)


class CatalogDataTests(unittest.TestCase):
    def test_real_tree_checks_clean(self):
        data = catalog.load_data()
        self.assertEqual(catalog.check_data(data), [])

    def test_every_tree_kit_is_in_the_data(self):
        data = catalog.load_data()
        self.assertEqual(
            sorted(catalog.data_kit_names(data)), catalog.tree_kit_names()
        )

    def test_missing_kit_is_caught(self):
        data = catalog.load_data()
        data["groups"][0]["kits"] = data["groups"][0]["kits"][1:]
        problems = catalog.check_data(data)
        self.assertTrue(any("missing from catalog data" in p for p in problems))

    def test_unknown_kit_is_caught(self):
        data = catalog.load_data()
        data["groups"][0]["kits"].append({"name": "NoSuchKit", "blurb": "x"})
        problems = catalog.check_data(data)
        self.assertTrue(any("does not exist" in p for p in problems))

    def test_download_urls_point_at_this_repo(self):
        url = catalog.download_url("SettingsKit", "0.1.0")
        self.assertEqual(
            url,
            "https://github.com/SeanShaffer88/WinDevKit/releases/download/"
            "SettingsKit-v0.1.0/SettingsKit-v0.1.0-x64.zip",
        )

    def test_rendered_catalog_covers_every_kit(self):
        data = catalog.load_data()
        text = catalog.render(data)
        for kit in catalog.tree_kit_names():
            self.assertIn(kit, text)
            self.assertIn(catalog.download_url(kit, catalog.kit_version(kit)), text)

    def test_rendered_catalog_never_links_a_standalone_kit_repo(self):
        # In-repo kits must not link to SeanShaffer88/<Kit> repos: those
        # repositories are gone, which is exactly how the catalog rotted.
        data = catalog.load_data()
        text = catalog.render(data)
        for kit in catalog.tree_kit_names():
            self.assertNotIn(f"github.com/SeanShaffer88/{kit}", text)

    def test_checked_in_catalog_is_current(self):
        data = catalog.load_data()
        self.assertEqual(
            (ROOT / "docs" / "CATALOG.md").read_text(encoding="utf-8"),
            catalog.render(data),
        )


if __name__ == "__main__":
    unittest.main()
