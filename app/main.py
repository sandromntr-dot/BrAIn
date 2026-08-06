from app.ai.embeddings import OllamaEmbeddingClient
from app.ai.gemma import GemmaClient
from app.core.config import Config
from app.database.connection import Database
from app.database.repository import DocumentRepository
from app.services.analyzer import AnalysisService, DocumentAnalyzer
from app.services.dashboard import DashboardService
from app.services.folders import FolderSettingsService
from app.services.history import AnalysisHistoryService
from app.services.indexer import Indexer
from app.services.search import SearchService
from app.ui.window import MainWindow


def main():

    database = Database()
    database.create_tables()
    repository = DocumentRepository(database)

    indexer = Indexer(repository)
    indexer.run()

    analyzer = DocumentAnalyzer(
        GemmaClient(),
        repository,
        visual_gemma_client=GemmaClient(model="gemma3:4b"),
    )
    analysis_service = AnalysisService(repository, analyzer)

    folder_service = FolderSettingsService(Config())
    window = MainWindow(
        SearchService(repository, OllamaEmbeddingClient()),
        analysis_service,
        folder_service=folder_service,
        dashboard_service=DashboardService(
            repository,
            AnalysisService.SUPPORTED_EXTENSIONS,
        ),
        history_service=AnalysisHistoryService(repository),
    )
    window.run()


if __name__ == "__main__":
    main()
