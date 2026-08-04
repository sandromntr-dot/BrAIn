import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from app.core.processor import (
    DocumentProcessingError,
    DocumentProcessor,
    DocxDocumentProcessor,
    TextDocumentProcessor,
)


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


class DocxDocumentProcessorTest(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_docx(self, name, paragraphs):
        path = self.root / name
        body = "".join(
            f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>"
            for paragraph in paragraphs
        )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/'
            'wordprocessingml/2006/main"><w:body>'
            f"{body}</w:body></w:document>"
        )

        with ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", xml)

        return path

    def test_extracts_docx_paragraphs(self):
        path = self.create_docx("document.docx", ["First", "Second"])

        content = DocxDocumentProcessor().extract(path)

        self.assertEqual(content, "First\nSecond")

    def test_rejects_invalid_docx(self):
        path = self.root / "invalid.docx"
        path.write_bytes(b"not-a-zip")

        with self.assertRaisesRegex(DocumentProcessingError, "ler o DOCX"):
            DocxDocumentProcessor().extract(path)

    def test_dispatches_supported_document_formats(self):
        path = self.create_docx("document.DOCX", ["Content"])

        content = DocumentProcessor().extract(path)

        self.assertEqual(content, "Content")
