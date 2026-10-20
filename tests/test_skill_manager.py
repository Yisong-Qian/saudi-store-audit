import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skill_manager", ROOT / "scripts/skill_manager.py")
manager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manager)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.source = self.root / "source"
        shutil.copytree(manager.SKILL_ROOT, self.source)

    def add_private_settings(self):
        (self.source / "references/store-config.local.json").write_text(
            json.dumps({"spreadsheet_url": "private-test-target"}), encoding="utf-8"
        )
        (self.source / ".env").write_text("DUMMY_PRIVATE_VALUE=test-only\n", encoding="utf-8")

    def test_install_copies_public_files_and_excludes_private_settings(self):
        self.add_private_settings()
        target = self.root / "installed"
        manager.install_bundle(target, self.source)
        actual = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()}
        self.assertEqual(actual, set(manager.PUBLIC_FILES))
        for name in manager.PUBLIC_FILES:
            self.assertEqual((target / name).read_bytes(), (self.source / name).read_bytes())

    def test_existing_installation_is_preserved(self):
        target = self.root / "existing"
        target.mkdir()
        sentinel = target / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            manager.install_bundle(target, self.source)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(list(target.iterdir()), [sentinel])

    def test_missing_public_file_is_rejected(self):
        (self.source / "references/writeback.md").unlink()
        with self.assertRaises(ValueError):
            manager.validate_bundle(self.source)

    def test_broken_relative_reference_is_rejected(self):
        path = self.source / "SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[missing](references/missing.md)\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            manager.validate_bundle(self.source)

    def test_public_config_cannot_ship_a_personal_target(self):
        path = self.source / "references/store-config.example.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["spreadsheet_url"] = "private-test-target"
        path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(ValueError):
            manager.validate_bundle(self.source)

    def test_zip_is_complete_and_excludes_local_files(self):
        self.add_private_settings()
        output = self.root / "bundle.zip"
        manager.package_bundle(output, self.source)
        with zipfile.ZipFile(output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), {manager.SKILL_NAME + "/" + n for n in manager.PUBLIC_FILES})
            for name in manager.PUBLIC_FILES:
                self.assertEqual(archive.read(manager.SKILL_NAME + "/" + name), (self.source / name).read_bytes())

    def test_zip_is_reproducible(self):
        first, second = self.root / "first.zip", self.root / "second.zip"
        manager.package_bundle(first, self.source)
        manager.package_bundle(second, self.source)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_acceptance_baseline_has_matching_case_ids(self):
        fixtures = ROOT / "tests/fixtures"
        inputs = json.loads((fixtures / "marking-cases.json").read_text(encoding="utf-8"))["cases"]
        expected = json.loads((fixtures / "expected-marking-decisions.json").read_text(encoding="utf-8"))["cases"]
        self.assertEqual({x["id"] for x in inputs}, {x["id"] for x in expected})
        self.assertEqual(len(expected), 19)
        self.assertTrue(all(x["historical_or_base_data_may_change"] is False for x in expected))


if __name__ == "__main__":
    unittest.main()
