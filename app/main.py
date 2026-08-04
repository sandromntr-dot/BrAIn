from app.core.scanner import Scanner


def main():

    scanner = Scanner(
        r"C:\Users\Admin\Downloads"
    )

    documents = scanner.scan()

    for document in documents:
        print(document)


if __name__ == "__main__":
    main()