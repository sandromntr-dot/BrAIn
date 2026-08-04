import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services.indexer import Indexer


class IndexerTest(unittest.TestCase):

    def test_reports_read_errors_without_interrupting_persistence(self):
        document = SimpleNamespace(name="document.txt")
        blocked_path = Path("blocked")

        scanner = Mock()
        scanner.scan.return_value = [document]
        scanner.errors = [(blocked_path, "access denied")]

        repository = Mock()
        repository.save.return_value = True
        repository.mark_missing.return_value = 0

        settings = {
            "monitor": {
                "downloads": True,
                "documents": False,
                "desktop": False,
            }
        }

        output = io.StringIO()

        with (
            patch("app.services.indexer.Config") as config_class,
            patch("app.services.indexer.Scanner", return_value=scanner),
            redirect_stdout(output),
        ):
            config_class.return_value.load.return_value = settings
            config_class.return_value.monitored_folders.return_value = [
                Path.home() / "Downloads"
            ]
            Indexer(repository).run()

        repository.save.assert_called_once_with(document)
        repository.mark_missing.assert_called_once()
        self.assertIn("Persistidos/atualizados: 1", output.getvalue())
        self.assertIn("Indisponiveis: 0", output.getvalue())
        self.assertIn(str(blocked_path), output.getvalue())
        self.assertIn("access denied", output.getvalue())

    def test_does_not_reconcile_missing_files_when_folder_is_unavailable(self):
        scanner = Mock()
        scanner.scan.return_value = []
        scanner.errors = []

        repository = Mock()
        missing_folder = Path("missing-home")
        settings = {
            "monitor": {
                "downloads": True,
                "documents": False,
                "desktop": False,
            }
        }

        with (
            patch("app.services.indexer.Config") as config_class,
            patch("app.services.indexer.Scanner", return_value=scanner),
            patch("pathlib.Path.exists", return_value=False),
            redirect_stdout(io.StringIO()),
        ):
            config_class.return_value.load.return_value = settings
            config_class.return_value.monitored_folders.return_value = [
                missing_folder
            ]
            Indexer(repository).run()

        repository.mark_missing.assert_not_called()


if __name__ == "__main__":
    unittest.main()
