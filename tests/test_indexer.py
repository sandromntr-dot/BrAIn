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
            Indexer(repository).run()

        repository.save.assert_called_once_with(document)
        self.assertIn("Persistidos/atualizados: 1", output.getvalue())
        self.assertIn(str(blocked_path), output.getvalue())
        self.assertIn("access denied", output.getvalue())


if __name__ == "__main__":
    unittest.main()
