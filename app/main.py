from app.database.connection import Database
from app.database.repository import DocumentRepository
from app.services.indexer import Indexer
from app.services.search import SearchService
from app.ui.window import MainWindow


def main():

    database = Database()
    database.create_tables()
    repository = DocumentRepository(database)

    indexer = Indexer(repository)
    indexer.run()

    window = MainWindow(SearchService(repository))
    window.run()


if __name__ == "__main__":
    main()
