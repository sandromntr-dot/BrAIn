from app.core.document import Document


def main():

    document = Document(
        name="manual.pdf",
        path="C:/Downloads/manual.pdf",
        extension=".pdf",
        size=5000
    )

    print(document)


if __name__ == "__main__":
    main()