from app.core.config import Config
from app.core.scanner import Scanner
from app.database.repository import DocumentRepository


class Indexer:

    def __init__(self, repository=None):
        self.repository = repository or DocumentRepository()

    def run(self):

        config = Config()
        settings = config.load()

        folders = config.monitored_folders(settings)

        for folder in folders:

            print(f"\nEscaneando: {folder}")

            scanner = Scanner(folder)
            documents = scanner.scan()

            print(f"Encontrados: {len(documents)}\n")

            persisted = 0
            unchanged = 0

            for document in documents:
                if self.repository.save(document):
                    persisted += 1
                else:
                    unchanged += 1

                print(f" - {document.name}")

            missing = 0

            if folder.exists():
                missing = self.repository.mark_missing(
                    folder,
                    (document.path for document in documents),
                    (path for path, _ in scanner.errors),
                )

            print(
                f"Persistidos/atualizados: {persisted} | "
                f"Sem alteracao: {unchanged} | "
                f"Indisponiveis: {missing} | "
                f"Falhas de leitura: {len(scanner.errors)}"
            )

            for path, reason in scanner.errors:
                print(f" ! {path}: {reason}")
