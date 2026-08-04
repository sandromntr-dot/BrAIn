import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.config import Config
from app.services.folders import FolderSettingsService


class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temporary_directory.name)
        self.config = Config()
        self.config.file = self.root / "settings.json"
        self.config.file.write_text("{}", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_loads_defaults_for_older_configuration(self):
        settings = self.config.load()

        self.assertTrue(settings["monitor"]["downloads"])
        self.assertTrue(settings["monitor"]["documents"])
        self.assertFalse(settings["monitor"]["desktop"])
        self.assertEqual(settings["custom_folders"], [])

    def test_resolves_standard_and_unique_custom_folders(self):
        custom = self.root / "custom"
        settings = {
            "monitor": {
                "downloads": True,
                "documents": False,
                "desktop": True,
            },
            "custom_folders": [str(custom), str(custom)],
            "frequency": "manual",
        }

        with patch("app.core.config.Path.home", return_value=self.root):
            folders = self.config.monitored_folders(settings)

        self.assertEqual(folders, [
            self.root / "Downloads",
            self.root / "Desktop",
            custom,
        ])

    def test_folder_service_persists_standard_and_custom_folders(self):
        first = self.root / "first"
        service = FolderSettingsService(self.config)

        saved = service.save(False, True, True, [first, first])
        persisted = json.loads(self.config.file.read_text(encoding="utf-8"))

        self.assertFalse(saved.downloads)
        self.assertTrue(saved.documents)
        self.assertTrue(saved.desktop)
        self.assertEqual(saved.custom_folders, (first.resolve(),))
        self.assertEqual(persisted["custom_folders"], [str(first.resolve())])


if __name__ == "__main__":
    unittest.main()
