from contextlib import closing

from app.database.connection import Database


class DocumentRepository:

    def __init__(self, database=None):
        self.database = database or Database()

    def save(self, document):
        with closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute("""
                    INSERT INTO documents
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
                    ON CONFLICT(path) DO UPDATE SET
                        name = excluded.name,
                        extension = excluded.extension,
                        size = excluded.size,
                        created_at = excluded.created_at,
                        summary = NULL,
                        category = NULL,
                        processed = 0,
                        indexed_at = datetime('now')
                    WHERE documents.name IS NOT excluded.name
                       OR documents.extension IS NOT excluded.extension
                       OR documents.size IS NOT excluded.size
                       OR documents.created_at IS NOT excluded.created_at
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
