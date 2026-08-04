from app.database.connection import Database


class DocumentRepository:

    def __init__(self):
        self.database = Database()

    def save(self, document):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO documents
            (
                name,
                path,
                extension,
                size,
                created_at,
                summary,
                category,
                indexed_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))

        """, (

            document.name,
            str(document.path),
            document.extension,
            document.size,
            str(document.created_at),
            None,
            None

        ))

        connection.commit()
        connection.close()