import sqlite3
from contextlib import closing
from pathlib import Path


class Database:

    def __init__(self):
        self.database = Path("data/brain.db")

    def connect(self):
        self.database.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.database)

    def create_tables(self):
        with closing(self.connect()) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        path TEXT UNIQUE NOT NULL,
                        extension TEXT,
                        size INTEGER,
                        created_at TEXT,
                        summary TEXT,
                        category TEXT,
                        processed INTEGER NOT NULL DEFAULT 0,
                        indexed_at TEXT NOT NULL,
                        available INTEGER NOT NULL DEFAULT 1,
                        missing_at TEXT,
                        analysis_error TEXT,
                        analysis_failed_at TEXT
                    );
                """)

                columns = {
                    row[1]
                    for row in connection.execute("PRAGMA table_info(documents)")
                }

                if "available" not in columns:
                    connection.execute("""
                        ALTER TABLE documents
                        ADD COLUMN available INTEGER NOT NULL DEFAULT 1
                    """)

                if "missing_at" not in columns:
                    connection.execute("""
                        ALTER TABLE documents
                        ADD COLUMN missing_at TEXT
                    """)

                if "analysis_error" not in columns:
                    connection.execute("""
                        ALTER TABLE documents
                        ADD COLUMN analysis_error TEXT
                    """)

                if "analysis_failed_at" not in columns:
                    connection.execute("""
                        ALTER TABLE documents
                        ADD COLUMN analysis_failed_at TEXT
                    """)
