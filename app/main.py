from app.core.scanner import Scanner
from app.utils.config import DOWNLOAD_FOLDER


def main():
    scanner = Scanner(DOWNLOAD_FOLDER)

    files = scanner.scan()

    for file in files:
        print(file.name)


if __name__ == "__main__":
    main()