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

    def fetch_one(self, query):
        connection = sqlite3.connect(self.database.database)
        try:
            return connection.execute(query).fetchone()
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


if __name__ == "__main__":
    unittest.main()
