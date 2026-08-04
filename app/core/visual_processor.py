import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pymupdf

from app.core.processor import DocumentProcessingError


@dataclass(frozen=True)
class VisualDocument:
    images: tuple[bytes, ...]
    total_pages: int
    truncated: bool = False


class VisualDocumentProcessor:

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | {".pdf", ".pptx"}
    MEDIA_PATTERN = re.compile(r"ppt/media/image(\d+)\.[^.]+$", re.IGNORECASE)

    def __init__(self, max_pages=20, pdf_dpi=144):
        if max_pages < 1 or pdf_dpi < 72:
            raise ValueError("visual processor limits are invalid")

        self.max_pages = max_pages
        self.pdf_dpi = pdf_dpi

    def supports(self, path):
        return Path(path).suffix.casefold() in self.SUPPORTED_EXTENSIONS

    def extract(self, path):
        path = Path(path)
        extension = path.suffix.casefold()

        if extension in self.IMAGE_EXTENSIONS:
            return self._extract_image(path)

        if extension == ".pdf":
            return self._extract_pdf(path)

        if extension == ".pptx":
            return self._extract_pptx(path)

        raise DocumentProcessingError(
            f"Formato visual ainda não suportado: {extension or 'sem extensão'}"
        )

    def page_count(self, path):
        path = Path(path)
        extension = path.suffix.casefold()

        if extension in self.IMAGE_EXTENSIONS:
            return 1

        if extension == ".pdf":
            try:
                with pymupdf.open(path) as document:
                    if document.needs_pass:
                        raise DocumentProcessingError(
                            f"PDF protegido por senha: {path}"
                        )
                    return document.page_count
            except DocumentProcessingError:
                raise
            except (OSError, RuntimeError, ValueError) as error:
                raise DocumentProcessingError(
                    f"Não foi possível ler o PDF {path}: {error}"
                ) from error

        if extension == ".pptx":
            return len(self._pptx_media(path))

        raise DocumentProcessingError(
            f"Formato visual ainda não suportado: {extension or 'sem extensão'}"
        )

    def extract_page(self, path, page_index):
        path = Path(path)
        total_pages = self.page_count(path)

        if page_index < 0 or page_index >= total_pages:
            raise IndexError("visual page index is out of range")

        extension = path.suffix.casefold()

        if extension in self.IMAGE_EXTENSIONS:
            return self._extract_image(path).images[0]

        if extension == ".pdf":
            try:
                with pymupdf.open(path) as document:
                    page = document.load_page(page_index)
                    pixmap = page.get_pixmap(dpi=self.pdf_dpi, alpha=False)
                    return pixmap.tobytes("jpeg", jpg_quality=80)
            except (OSError, RuntimeError, ValueError) as error:
                raise DocumentProcessingError(
                    f"Não foi possível renderizar a página do PDF {path}: {error}"
                ) from error

        media = self._pptx_media(path)

        try:
            with ZipFile(path) as archive:
                return archive.read(media[page_index][1])
        except (OSError, BadZipFile) as error:
            raise DocumentProcessingError(
                f"Não foi possível ler o slide do PPTX {path}: {error}"
            ) from error

    @staticmethod
    def _extract_image(path):
        try:
            content = path.read_bytes()
        except OSError as error:
            raise DocumentProcessingError(
                f"Não foi possível ler a imagem {path}: {error}"
            ) from error

        if not content:
            raise DocumentProcessingError(f"A imagem está vazia: {path}")

        return VisualDocument(images=(content,), total_pages=1)

    def _extract_pdf(self, path):
        try:
            document = pymupdf.open(path)

            if document.needs_pass:
                raise DocumentProcessingError(f"PDF protegido por senha: {path}")

            total_pages = document.page_count
            images = []

            for page_number in range(min(total_pages, self.max_pages)):
                page = document.load_page(page_number)
                pixmap = page.get_pixmap(dpi=self.pdf_dpi, alpha=False)
                images.append(pixmap.tobytes("jpeg", jpg_quality=80))
        except DocumentProcessingError:
            raise
        except (OSError, RuntimeError, ValueError) as error:
            raise DocumentProcessingError(
                f"Não foi possível renderizar o PDF {path}: {error}"
            ) from error
        finally:
            if "document" in locals():
                document.close()

        if not images:
            raise DocumentProcessingError(f"O PDF não possui páginas: {path}")

        return VisualDocument(
            images=tuple(images),
            total_pages=total_pages,
            truncated=total_pages > self.max_pages,
        )

    def _extract_pptx(self, path):
        media = self._pptx_media(path)

        try:
            with ZipFile(path) as archive:
                total_pages = len(media)
                images = tuple(
                    archive.read(info)
                    for _, info in media[:self.max_pages]
                )
        except (OSError, BadZipFile) as error:
            raise DocumentProcessingError(
                f"Não foi possível extrair imagens do PPTX {path}: {error}"
            ) from error

        if not images:
            raise DocumentProcessingError(
                f"O PPTX não contém imagens compatíveis: {path}"
            )

        return VisualDocument(
            images=images,
            total_pages=total_pages,
            truncated=total_pages > self.max_pages,
        )

    def _pptx_media(self, path):
        try:
            with ZipFile(path) as archive:
                media = []

                for info in archive.infolist():
                    match = self.MEDIA_PATTERN.fullmatch(info.filename)

                    if (
                        match
                        and Path(info.filename).suffix.casefold()
                        in self.IMAGE_EXTENSIONS
                    ):
                        media.append((int(match.group(1)), info))
        except (OSError, BadZipFile) as error:
            raise DocumentProcessingError(
                f"Não foi possível extrair imagens do PPTX {path}: {error}"
            ) from error

        media.sort(key=lambda item: item[0])

        if not media:
            raise DocumentProcessingError(
                f"O PPTX não contém imagens compatíveis: {path}"
            )

        return media
