from pathlib import Path

from app.core.config import Config
from app.core.scanner import Scanner
from app.database.repository import DocumentRepository


class Indexer:

    def __init__(self, repository=None):
        self.repository = repository or DocumentRepository()

    def run(self):

        config = Config()
        settings = config.load()

        folders = []

        monitor = settings["monitor"]

        if monitor["downloads"]:
            folders.append(Path.home() / "Downloads")

        if monitor["documents"]:
            folders.append(Path.home() / "Documents")

        if monitor["desktop"]:
            folders.append(Path.home() / "Desktop")

        for folder in folders:

            print(f"\nEscaneando: {folder}")

            scanner = Scanner(folder)
            documents = scanner.scan()

            print(f"Encontrados: {len(documents)}\n")

            for document in documents:
                self.repository.save(document)
                print(f" - {document.name}")
