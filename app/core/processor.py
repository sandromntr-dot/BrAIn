from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


class DocumentProcessingError(RuntimeError):
    """Erro ao extrair conteúdo de um documento."""


class TextDocumentProcessor:

    def __init__(self, max_characters=6_000):
        if max_characters < 1:
            raise ValueError("max_characters must be greater than zero")

        self.max_characters = max_characters

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".txt":
            raise DocumentProcessingError(
                f"Formato ainda não suportado: {path.suffix or 'sem extensão'}"
            )

        try:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="cp1252")
        except OSError as error:
            raise DocumentProcessingError(
                f"Não foi possível ler {path}: {error}"
            ) from error

        content = content.strip()

        if not content:
            raise DocumentProcessingError(f"O documento está vazio: {path}")

        return content[:self.max_characters]


class DocxDocumentProcessor:

    DOCUMENT_XML = "word/document.xml"
    WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    def __init__(self, max_characters=6_000, max_xml_bytes=5_000_000):
        if max_characters < 1 or max_xml_bytes < 1:
            raise ValueError("processor limits must be greater than zero")

        self.max_characters = max_characters
        self.max_xml_bytes = max_xml_bytes

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".docx":
            raise DocumentProcessingError(
                f"Formato ainda não suportado: {path.suffix or 'sem extensão'}"
            )

        try:
            with ZipFile(path) as archive:
                info = archive.getinfo(self.DOCUMENT_XML)

                if info.file_size > self.max_xml_bytes:
                    raise DocumentProcessingError(
                        f"Conteúdo interno muito grande: {path}"
                    )

                xml = archive.read(info)
        except (OSError, BadZipFile, KeyError) as error:
            raise DocumentProcessingError(
                f"Não foi possível ler o DOCX {path}: {error}"
            ) from error

        try:
            root = ElementTree.fromstring(xml)
        except ElementTree.ParseError as error:
            raise DocumentProcessingError(f"DOCX inválido: {path}") from error

        paragraphs = []

        for paragraph in root.iter(f"{self.WORD_NAMESPACE}p"):
            text = "".join(
                node.text or ""
                for node in paragraph.iter(f"{self.WORD_NAMESPACE}t")
            ).strip()

            if text:
                paragraphs.append(text)

        content = "\n".join(paragraphs).strip()

        if not content:
            raise DocumentProcessingError(f"O documento está vazio: {path}")

        return content[:self.max_characters]


class DocumentProcessor:

    def __init__(self, max_characters=6_000):
        self.processors = {
            ".txt": TextDocumentProcessor(max_characters),
            ".docx": DocxDocumentProcessor(max_characters),
        }

    def extract(self, path):
        path = Path(path)
        processor = self.processors.get(path.suffix.casefold())

        if processor is None:
            raise DocumentProcessingError(
                f"Formato ainda não suportado: {path.suffix or 'sem extensão'}"
            )

        return processor.extract(path)
