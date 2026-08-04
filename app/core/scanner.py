from pathlib import Path

from app.core.document import Document


class Scanner:
    """Responsável por localizar documentos."""

    def __init__(self, folder: str):
        self.folder = Path(folder)

    def scan(self) -> list[Document]:
        """Retorna documentos encontrados."""

        if not self.folder.exists():
            return []

        return [
            Document(file)
            for file in self.folder.iterdir()
            if file.is_file()
        ]