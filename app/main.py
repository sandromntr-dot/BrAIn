from app.services.indexer import Indexer


def main():

    indexer = Indexer()
    indexer.run()


if __name__ == "__main__":
    main()