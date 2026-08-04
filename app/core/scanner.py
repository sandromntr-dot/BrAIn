import os
from pathlib import Path

from app.core.document import Document


class Scanner:
    """Responsável por localizar documentos."""

    def __init__(self, folder: str):
        self.folder = Path(folder)
        self.errors: list[tuple[Path, str]] = []

    def scan(self) -> list[Document]:
        """Retorna documentos encontrados."""

        self.errors.clear()

        if not self.folder.exists():
            return []

        documents = []

        for root, directories, filenames in os.walk(
            self.folder,
            onerror=self._record_walk_error,
        ):
            directories.sort()
            filenames.sort()

            for filename in filenames:
                path = Path(root) / filename

                try:
                    if path.is_file():
                        documents.append(Document(path))
                except OSError as error:
                    self.errors.append((path, str(error)))

        return documents

    def _record_walk_error(self, error: OSError):
        path = Path(error.filename) if error.filename else self.folder
        self.errors.append((path, str(error)))
