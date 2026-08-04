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
                        indexed_at TEXT NOT NULL
                    );
                """)
