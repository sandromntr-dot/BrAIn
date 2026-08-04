from app.ai.gemma import GemmaClient
from app.core.config import Config
from app.database.connection import Database
from app.database.repository import DocumentRepository
from app.services.analyzer import AnalysisService, DocumentAnalyzer
from app.services.folders import FolderSettingsService
from app.services.indexer import Indexer
from app.services.search import SearchService
from app.ui.window import MainWindow


def main():

    database = Database()
    database.create_tables()
    repository = DocumentRepository(database)

    indexer = Indexer(repository)
    indexer.run()

    analyzer = DocumentAnalyzer(GemmaClient(), repository)
    analysis_service = AnalysisService(repository, analyzer)

    folder_service = FolderSettingsService(Config())
    window = MainWindow(
        SearchService(repository),
        analysis_service,
        folder_service=folder_service,
    )
    window.run()


if __name__ == "__main__":
    main()
