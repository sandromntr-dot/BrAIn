import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.document import Document
from app.core.scanner import Scanner


class ScannerTest(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_scans_files_recursively(self):
        nested_folder = self.root / "folder" / "nested"
        nested_folder.mkdir(parents=True)
        (self.root / "root.txt").write_text("root", encoding="utf-8")
        (nested_folder / "nested.pdf").write_bytes(b"pdf")

        scanner = Scanner(self.root)

        documents = scanner.scan()

        paths = {document.path for document in documents}
        self.assertEqual(paths, {
            self.root / "root.txt",
            nested_folder / "nested.pdf",
        })
        self.assertEqual(scanner.errors, [])

    def test_returns_empty_list_for_missing_folder(self):
        scanner = Scanner(self.root / "missing")

        documents = scanner.scan()

        self.assertEqual(documents, [])
        self.assertEqual(scanner.errors, [])

    def test_continues_when_a_document_cannot_be_read(self):
        blocked_path = self.root / "blocked.txt"
        readable_path = self.root / "readable.txt"
        blocked_path.write_text("blocked", encoding="utf-8")
        readable_path.write_text("readable", encoding="utf-8")

        def create_document(path):
            if path == blocked_path:
                raise PermissionError("access denied")
            return Document(path)

        scanner = Scanner(self.root)

        with patch("app.core.scanner.Document", side_effect=create_document):
            documents = scanner.scan()

        self.assertEqual([document.path for document in documents], [readable_path])
        self.assertEqual(scanner.errors, [(blocked_path, "access denied")])


if __name__ == "__main__":
    unittest.main()
