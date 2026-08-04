import tempfile
import unittest
from pathlib import Path

from app.core.processor import DocumentProcessingError, TextDocumentProcessor


class TextDocumentProcessorTest(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_extracts_and_limits_utf8_text(self):
        path = self.root / "document.txt"
        path.write_text("  conteúdo longo  ", encoding="utf-8")

        content = TextDocumentProcessor(max_characters=8).extract(path)

        self.assertEqual(content, "conteúdo")

    def test_reads_legacy_windows_encoding(self):
        path = self.root / "document.txt"
        path.write_bytes("ação".encode("cp1252"))

        content = TextDocumentProcessor().extract(path)

        self.assertEqual(content, "ação")

    def test_rejects_unsupported_format(self):
        path = self.root / "document.pdf"
        path.write_bytes(b"pdf")

        with self.assertRaisesRegex(DocumentProcessingError, "não suportado"):
            TextDocumentProcessor().extract(path)

    def test_rejects_empty_document(self):
        path = self.root / "document.txt"
        path.write_text("   ", encoding="utf-8")

        with self.assertRaisesRegex(DocumentProcessingError, "vazio"):
            TextDocumentProcessor().extract(path)
