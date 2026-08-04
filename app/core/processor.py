import csv
import io
import re
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader
from pypdf.errors import PyPdfError


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


class PdfDocumentProcessor:

    def __init__(self, max_characters=6_000):
        if max_characters < 1:
            raise ValueError("max_characters must be greater than zero")

        self.max_characters = max_characters

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".pdf":
            raise DocumentProcessingError(
                f"Formato ainda não suportado: {path.suffix or 'sem extensão'}"
            )

        try:
            reader = PdfReader(path, strict=False)

            if reader.is_encrypted:
                raise DocumentProcessingError(
                    f"PDF protegido por senha: {path}"
                )

            parts = []
            extracted_characters = 0

            for page in reader.pages:
                text = (page.extract_text() or "").strip()

                if not text:
                    continue

                separator_size = 1 if parts else 0
                remaining = (
                    self.max_characters
                    - extracted_characters
                    - separator_size
                )

                if remaining <= 0:
                    break

                parts.append(text[:remaining])
                extracted_characters += len(parts[-1]) + separator_size

                if extracted_characters >= self.max_characters:
                    break
        except DocumentProcessingError:
            raise
        except (OSError, PyPdfError) as error:
            raise DocumentProcessingError(
                f"Não foi possível ler o PDF {path}: {error}"
            ) from error

        content = "\n".join(parts).strip()

        if not content:
            raise DocumentProcessingError(
                f"O PDF não contém texto extraível e pode exigir OCR: {path}"
            )

        return content


class CsvDocumentProcessor:

    def __init__(self, max_characters=6_000, max_bytes=1_000_000, max_rows=200):
        self.max_characters = max_characters
        self.max_bytes = max_bytes
        self.max_rows = max_rows

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".csv":
            raise DocumentProcessingError(f"Formato ainda não suportado: {path.suffix}")

        try:
            with path.open("rb") as file:
                raw = file.read(self.max_bytes + 1)
        except OSError as error:
            raise DocumentProcessingError(f"Não foi possível ler o CSV {path}: {error}") from error

        if len(raw) > self.max_bytes:
            raw = raw[:self.max_bytes]

        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")

        try:
            dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel

        rows = []

        for index, row in enumerate(csv.reader(io.StringIO(text), dialect)):
            if index >= self.max_rows:
                break

            normalized = " | ".join(cell.strip() for cell in row).strip()

            if normalized:
                rows.append(normalized)

            if len("\n".join(rows)) >= self.max_characters:
                break

        content = "\n".join(rows).strip()[:self.max_characters]

        if not content:
            raise DocumentProcessingError(f"O documento está vazio: {path}")

        return content


class BpmnDocumentProcessor:

    RELEVANT_ELEMENTS = {
        "process": "Processo",
        "task": "Tarefa",
        "userTask": "Tarefa de usuário",
        "serviceTask": "Tarefa de serviço",
        "sendTask": "Tarefa de envio",
        "receiveTask": "Tarefa de recebimento",
        "manualTask": "Tarefa manual",
        "businessRuleTask": "Regra de negócio",
        "scriptTask": "Script",
        "startEvent": "Evento inicial",
        "endEvent": "Evento final",
        "intermediateCatchEvent": "Evento intermediário",
        "exclusiveGateway": "Gateway exclusivo",
        "parallelGateway": "Gateway paralelo",
        "inclusiveGateway": "Gateway inclusivo",
        "subProcess": "Subprocesso",
    }

    def __init__(self, max_characters=6_000, max_bytes=5_000_000):
        self.max_characters = max_characters
        self.max_bytes = max_bytes

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".bpmn":
            raise DocumentProcessingError(f"Formato ainda não suportado: {path.suffix}")

        try:
            if path.stat().st_size > self.max_bytes:
                raise DocumentProcessingError(f"Arquivo BPMN muito grande: {path}")

            root = ElementTree.parse(path).getroot()
        except DocumentProcessingError:
            raise
        except (OSError, ElementTree.ParseError) as error:
            raise DocumentProcessingError(f"Não foi possível ler o BPMN {path}: {error}") from error

        lines = []

        for element in root.iter():
            element_type = element.tag.rsplit("}", 1)[-1]
            name = element.attrib.get("name") or element.attrib.get("id")

            if element_type in self.RELEVANT_ELEMENTS and name:
                lines.append(f"{self.RELEVANT_ELEMENTS[element_type]}: {name}")
            elif element_type == "sequenceFlow":
                source = element.attrib.get("sourceRef", "?")
                target = element.attrib.get("targetRef", "?")
                flow_name = element.attrib.get("name")
                suffix = f" ({flow_name})" if flow_name else ""
                lines.append(f"Fluxo: {source} -> {target}{suffix}")

            if len("\n".join(lines)) >= self.max_characters:
                break

        content = "\n".join(lines).strip()[:self.max_characters]

        if not content:
            raise DocumentProcessingError(f"O BPMN não contém elementos reconhecidos: {path}")

        return content


class PptxDocumentProcessor:

    DRAWING_NAMESPACE = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    SLIDE_PATTERN = re.compile(r"ppt/slides/slide(\d+)\.xml$")

    def __init__(self, max_characters=6_000, max_xml_bytes=10_000_000):
        self.max_characters = max_characters
        self.max_xml_bytes = max_xml_bytes

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".pptx":
            raise DocumentProcessingError(f"Formato ainda não suportado: {path.suffix}")

        try:
            with ZipFile(path) as archive:
                slides = [
                    (int(match.group(1)), info)
                    for info in archive.infolist()
                    if (match := self.SLIDE_PATTERN.fullmatch(info.filename))
                ]
                slides.sort(key=lambda item: item[0])
                parts = []
                xml_bytes = 0

                for number, info in slides:
                    xml_bytes += info.file_size

                    if xml_bytes > self.max_xml_bytes:
                        raise DocumentProcessingError(f"Conteúdo interno muito grande: {path}")

                    root = ElementTree.fromstring(archive.read(info))
                    text = " ".join(
                        node.text or ""
                        for node in root.iter(f"{self.DRAWING_NAMESPACE}t")
                    ).strip()

                    if text:
                        parts.append(f"Slide {number}: {text}")

                    if len("\n".join(parts)) >= self.max_characters:
                        break
        except DocumentProcessingError:
            raise
        except (OSError, BadZipFile, ElementTree.ParseError) as error:
            raise DocumentProcessingError(f"Não foi possível ler o PPTX {path}: {error}") from error

        content = "\n".join(parts).strip()[:self.max_characters]

        if not content:
            raise DocumentProcessingError(
                "A apresentação não contém texto extraível e pode exigir OCR: "
                f"{path}"
            )

        return content


class DocumentProcessor:

    def __init__(self, max_characters=6_000):
        self.processors = {
            ".txt": TextDocumentProcessor(max_characters),
            ".docx": DocxDocumentProcessor(max_characters),
            ".pdf": PdfDocumentProcessor(max_characters),
            ".csv": CsvDocumentProcessor(max_characters),
            ".bpmn": BpmnDocumentProcessor(max_characters),
            ".pptx": PptxDocumentProcessor(max_characters),
        }

    def extract(self, path):
        path = Path(path)
        processor = self.processors.get(path.suffix.casefold())

        if processor is None:
            raise DocumentProcessingError(
                f"Formato ainda não suportado: {path.suffix or 'sem extensão'}"
            )

        return processor.extract(path)
