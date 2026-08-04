from pathlib import Path
from datetime import datetime


class Document:
    """Representa um documento encontrado pelo BrAIn."""

    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.extension = path.suffix
        self.size = path.stat().st_size
        self.created_at = datetime.fromtimestamp(
            path.stat().st_ctime
        )

    @property
    def size_mb(self):
        return round(
            self.size / (1024 * 1024),
            2
        )

    def __str__(self):
        return (
            f"Document("
            f"name='{self.name}', "
            f"extension='{self.extension}', "
            f"size={self.size_mb} MB, "
            f"created_at={self.created_at}"
            f")"
        )