from contextlib import closing
from pathlib import Path

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
                        indexed_at,
                        available,
                        missing_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 1, NULL)
                    ON CONFLICT(path) DO UPDATE SET
                        name = excluded.name,
                        extension = excluded.extension,
                        size = excluded.size,
                        created_at = excluded.created_at,
                        summary = NULL,
                        category = NULL,
                        processed = 0,
                        indexed_at = datetime('now'),
                        available = 1,
                        missing_at = NULL
                    WHERE documents.name IS NOT excluded.name
                       OR documents.extension IS NOT excluded.extension
                       OR documents.size IS NOT excluded.size
                       OR documents.created_at IS NOT excluded.created_at
                       OR documents.available = 0
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

    def mark_missing(self, folder, present_paths, unreadable_paths=()):
        folder = Path(folder).resolve(strict=False)
        present = {
            self._normalized_path(path)
            for path in present_paths
        }
        unreadable = [
            Path(path).resolve(strict=False)
            for path in unreadable_paths
        ]

        with closing(self.database.connect()) as connection:
            rows = connection.execute("""
                SELECT path
                FROM documents
                WHERE available = 1
            """).fetchall()

            missing = []

            for (stored_path,) in rows:
                path = Path(stored_path).resolve(strict=False)

                if not path.is_relative_to(folder):
                    continue

                if self._normalized_path(path) in present:
                    continue

                if any(
                    path == blocked_path or path.is_relative_to(blocked_path)
                    for blocked_path in unreadable
                ):
                    continue

                missing.append(stored_path)

            with connection:
                connection.executemany("""
                    UPDATE documents
                    SET available = 0, missing_at = datetime('now')
                    WHERE path = ?
                """, ((path,) for path in missing))

        return len(missing)

    @staticmethod
    def _normalized_path(path):
        return str(Path(path).resolve(strict=False)).casefold()
