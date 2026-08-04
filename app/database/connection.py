import sqlite3
from pathlib import Path


class Database:

    def __init__(self):
        self.database = Path("data/brain.db")

    def connect(self):
        return sqlite3.connect(self.database)

    def create_tables(self):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                path TEXT UNIQUE NOT NULL,

                extension TEXT,

                size INTEGER,

                created_at TEXT,

                summary TEXT,

                category TEXT,

                processed INTEGER DEFAULT 0,

                indexed_at TEXT

            );
        """)

        connection.commit()
        connection.close()