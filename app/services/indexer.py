from app.core.config import Config
from app.core.scanner import Scanner


class Indexer:

    def run(self):

        config = Config()
        settings = config.load()

        for folder in settings["folders"]:

            scanner = Scanner(folder)

            documents = scanner.scan()

            for document in documents:
                print(document)