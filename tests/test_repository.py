import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.core.document import Document
from app.database.connection import Database
from app.database.repository import DocumentRepository


class DocumentRepositoryTest(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temporary_directory.name)

        self.database = Database()
        self.database.database = self.root / "test.db"
        self.database.create_tables()

        self.repository = DocumentRepository(self.database)
        self.document_path = self.root / "example.txt"
        self.document_path.write_text("initial", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def fetch_one(self, query, parameters=()):
        connection = sqlite3.connect(self.database.database)
        try:
            return connection.execute(query, parameters).fetchone()
        finally:
            connection.close()

    def test_saves_all_document_fields(self):
        document = Document(self.document_path)

        saved = self.repository.save(document)

        row = self.fetch_one("""
            SELECT name, path, extension, size, created_at,
                   summary, category, processed, indexed_at
            FROM documents
        """)

        self.assertTrue(saved)
        self.assertEqual(row[0], document.name)
        self.assertEqual(row[1], str(document.path))
        self.assertEqual(row[2], document.extension)
        self.assertEqual(row[3], document.size)
        self.assertEqual(row[4], document.created_at.isoformat())
        self.assertIsNone(row[5])
        self.assertIsNone(row[6])
        self.assertEqual(row[7], 0)
        self.assertIsNotNone(row[8])

    def test_does_not_duplicate_unchanged_document(self):
        document = Document(self.document_path)

        first_save = self.repository.save(document)
        second_save = self.repository.save(document)

        count = self.fetch_one("SELECT COUNT(*) FROM documents")[0]

        self.assertTrue(first_save)
        self.assertFalse(second_save)
        self.assertEqual(count, 1)

    def test_updates_changed_document_and_resets_processing(self):
        self.repository.save(Document(self.document_path))

        connection = sqlite3.connect(self.database.database)
        try:
            connection.execute("""
                UPDATE documents
                SET summary = 'summary', category = 'test', processed = 1
            """)
            connection.commit()
        finally:
            connection.close()

        self.document_path.write_text("changed document content", encoding="utf-8")
        changed_document = Document(self.document_path)

        updated = self.repository.save(changed_document)

        row = self.fetch_one("""
            SELECT COUNT(*), size, summary, category, processed
            FROM documents
        """)

        self.assertTrue(updated)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], changed_document.size)
        self.assertIsNone(row[2])
        self.assertIsNone(row[3])
        self.assertEqual(row[4], 0)

    def test_marks_missing_document_and_restores_it_when_found_again(self):
        self.repository.save(Document(self.document_path))
        self.document_path.unlink()

        missing = self.repository.mark_missing(self.root, [])

        unavailable_row = self.fetch_one("""
            SELECT available, missing_at
            FROM documents
        """)

        self.document_path.write_text("initial", encoding="utf-8")
        restored = self.repository.save(Document(self.document_path))
        restored_row = self.fetch_one("""
            SELECT available, missing_at
            FROM documents
        """)

        self.assertEqual(missing, 1)
        self.assertEqual(unavailable_row[0], 0)
        self.assertIsNotNone(unavailable_row[1])
        self.assertTrue(restored)
        self.assertEqual(restored_row, (1, None))

    def test_does_not_mark_document_below_unreadable_folder_as_missing(self):
        blocked_folder = self.root / "blocked"
        blocked_folder.mkdir()
        blocked_document = blocked_folder / "document.txt"
        blocked_document.write_text("blocked", encoding="utf-8")
        self.repository.save(Document(blocked_document))

        missing = self.repository.mark_missing(
            self.root,
            [],
            [blocked_folder],
        )

        available = self.fetch_one("""
            SELECT available
            FROM documents
            WHERE path = ?
        """, (str(blocked_document),))[0]

        self.assertEqual(missing, 0)
        self.assertEqual(available, 1)

    def test_migrates_existing_database_for_availability_fields(self):
        legacy_database = Database()
        legacy_database.database = self.root / "legacy.db"

        connection = sqlite3.connect(legacy_database.database)
        try:
            connection.execute("""
                CREATE TABLE documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT UNIQUE NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    created_at TEXT,
                    summary TEXT,
                    category TEXT,
                    processed INTEGER NOT NULL DEFAULT 0,
                    indexed_at TEXT NOT NULL
                )
            """)
            connection.commit()
        finally:
            connection.close()

        legacy_database.create_tables()

        connection = sqlite3.connect(legacy_database.database)
        try:
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(documents)")
            }
        finally:
            connection.close()

        self.assertIn("available", columns)
        self.assertIn("missing_at", columns)

    def test_searches_available_documents_by_metadata(self):
        matching_path = self.root / "Architecture Guide.PDF"
        other_path = self.root / "notes.txt"
        matching_path.write_text("architecture", encoding="utf-8")
        other_path.write_text("notes", encoding="utf-8")
        self.repository.save(Document(matching_path))
        self.repository.save(Document(other_path))

        results = self.repository.search("architecture")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, matching_path.name)
        self.assertEqual(results[0].path, matching_path)
        self.assertTrue(results[0].available)

    def test_search_excludes_unavailable_documents(self):
        self.repository.save(Document(self.document_path))
        self.document_path.unlink()
        self.repository.mark_missing(self.root, [])

        results = self.repository.search("example")

        self.assertEqual(results, [])

    def test_search_treats_sql_wildcards_as_literal_characters(self):
        percent_path = self.root / "report_100%.txt"
        other_path = self.root / "report_1000.txt"
        percent_path.write_text("percent", encoding="utf-8")
        other_path.write_text("other", encoding="utf-8")
        self.repository.save(Document(percent_path))
        self.repository.save(Document(other_path))

        results = self.repository.search("100%")

        self.assertEqual([result.path for result in results], [percent_path])

    def test_search_rejects_invalid_limit(self):
        with self.assertRaises(ValueError):
            self.repository.search("document", limit=0)


if __name__ == "__main__":
    unittest.main()
