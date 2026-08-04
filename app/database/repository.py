from contextlib import closing
from pathlib import Path

from app.database.connection import Database
from app.database.models import StoredDocument


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
                        missing_at,
                        analysis_error,
                        analysis_failed_at
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 1, NULL, NULL, NULL
                    )
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
                        missing_at = NULL,
                        analysis_error = NULL,
                        analysis_failed_at = NULL
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

                if cursor.rowcount == 1:
                    connection.execute("""
                        DELETE FROM visual_analysis_chunks
                        WHERE document_path = ?
                    """, (str(document.path),))

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

    def search(self, query, limit=50):
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        escaped_query = self._escape_like(query.strip())
        pattern = f"%{escaped_query}%"

        with closing(self.database.connect()) as connection:
            rows = connection.execute("""
                SELECT
                    id,
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
                    missing_at,
                    analysis_error,
                    analysis_failed_at
                FROM documents
                WHERE available = 1
                  AND (
                      ? = ''
                      OR name LIKE ? ESCAPE '!'
                      OR path LIKE ? ESCAPE '!'
                      OR extension LIKE ? ESCAPE '!'
                      OR summary LIKE ? ESCAPE '!'
                      OR category LIKE ? ESCAPE '!'
                  )
                ORDER BY name COLLATE NOCASE, path COLLATE NOCASE
                LIMIT ?
            """, (
                escaped_query,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                limit,
            )).fetchall()

        return [self._to_stored_document(row) for row in rows]

    def pending_analysis(self, extension=".txt", limit=10):
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        with closing(self.database.connect()) as connection:
            rows = connection.execute("""
                SELECT
                    id,
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
                    missing_at,
                    analysis_error,
                    analysis_failed_at
                FROM documents
                WHERE available = 1
                  AND processed = 0
                  AND analysis_error IS NULL
                  AND extension = ? COLLATE NOCASE
                ORDER BY indexed_at, id
                LIMIT ?
            """, (extension, limit)).fetchall()

        return [self._to_stored_document(row) for row in rows]

    def count_pending_analysis(self, extension=".txt"):
        with closing(self.database.connect()) as connection:
            return connection.execute("""
                SELECT COUNT(*)
                FROM documents
                WHERE available = 1
                  AND processed = 0
                  AND analysis_error IS NULL
                  AND extension = ? COLLATE NOCASE
            """, (extension,)).fetchone()[0]

    def save_analysis(self, path, summary, category):
        with closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute("""
                    UPDATE documents
                    SET summary = ?,
                        category = ?,
                        processed = 1,
                        analysis_error = NULL,
                        analysis_failed_at = NULL
                    WHERE path = ? AND available = 1
                """, (summary, category, str(path)))

        return cursor.rowcount == 1

    def save_analysis_error(self, path, error):
        message = str(error).strip()[:1000] or "Falha de análise sem detalhes"

        with closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute("""
                    UPDATE documents
                    SET analysis_error = ?,
                        analysis_failed_at = datetime('now'),
                        processed = 0
                    WHERE path = ? AND available = 1
                """, (message, str(path)))

        return cursor.rowcount == 1

    def visual_analysis_chunks(self, path):
        with closing(self.database.connect()) as connection:
            rows = connection.execute("""
                SELECT chunk_index, content
                FROM visual_analysis_chunks
                WHERE document_path = ?
                ORDER BY chunk_index
            """, (str(path),)).fetchall()

        return {index: content for index, content in rows}

    def save_visual_analysis_chunk(self, path, chunk_index, content):
        if chunk_index < 0 or not content.strip():
            raise ValueError("visual chunk must have valid index and content")

        with closing(self.database.connect()) as connection:
            with connection:
                connection.execute("""
                    INSERT INTO visual_analysis_chunks
                        (document_path, chunk_index, content)
                    VALUES (?, ?, ?)
                    ON CONFLICT(document_path, chunk_index) DO UPDATE SET
                        content = excluded.content,
                        created_at = datetime('now')
                """, (str(path), chunk_index, content.strip()))

    def clear_visual_analysis_chunks(self, path):
        with closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute("""
                    DELETE FROM visual_analysis_chunks
                    WHERE document_path = ?
                """, (str(path),))

        return cursor.rowcount

    @staticmethod
    def _normalized_path(path):
        return str(Path(path).resolve(strict=False)).casefold()

    @staticmethod
    def _escape_like(value):
        return value.replace("!", "!!").replace("%", "!%").replace("_", "!_")

    @staticmethod
    def _to_stored_document(row):
        return StoredDocument(
            id=row[0],
            name=row[1],
            path=Path(row[2]),
            extension=row[3],
            size=row[4],
            created_at=row[5],
            summary=row[6],
            category=row[7],
            processed=bool(row[8]),
            indexed_at=row[9],
            available=bool(row[10]),
            missing_at=row[11],
            analysis_error=row[12],
            analysis_failed_at=row[13],
        )
