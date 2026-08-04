from app.database.connection import Database
from app.services.indexer import Indexer


def main():

    database = Database()
    database.create_tables()

    indexer = Indexer()
    indexer.run()


if __name__ == "__main__":
    main()