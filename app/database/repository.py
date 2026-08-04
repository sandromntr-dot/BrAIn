from contextlib import closing

from app.database.connection import Database


class DocumentRepository:

    def __init__(self, database=None):
        self.database = database or Database()

    def save(self, document):
        with closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute("""
                    INSERT OR IGNORE INTO documents
                    (
                        name,
                        path,
                        extension,
                        size,
                        created_at,
                        summary,
                        category,
                        processed,
                        indexed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    document.name,
                    str(document.path),
                    document.extension,
                    document.size,
                    document.created_at.isoformat(),
                    getattr(document, "summary", None),
                    getattr(document, "category", None),
                    int(getattr(document, "processed", False)),
                ))

            return cursor.rowcount == 1
