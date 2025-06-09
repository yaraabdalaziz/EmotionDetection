import sqlite3
from contextlib import contextmanager
import threading
from typing import Generator


class DatabaseManager:
    def __init__(self, db_path: str = "Database/emotion_detection.db") -> None:
        self.db_path = db_path
        self.local = threading.local()
        self._init_database()

    def _init_database(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    api_key TEXT NOT NULL UNIQUE,
                    quota INTEGER DEFAULT 50,
                    available_requests INTEGER DEFAULT 50
                );
                
                CREATE TABLE IF NOT EXISTS requests_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    probability REAL,        
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_api_key ON users(api_key);
                CREATE INDEX IF NOT EXISTS idx_user_requests ON requests_records(user_id);
            """
            )

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get thread-local database connection"""
        if not hasattr(self.local, "connection"):
            self.local.connection = sqlite3.connect(
                self.db_path, timeout=10.0, check_same_thread=False
            )
            self.local.connection.row_factory = sqlite3.Row

            self.local.connection.execute("PRAGMA journal_mode=WAL")
            self.local.connection.execute("PRAGMA synchronous=NORMAL")
            self.local.connection.execute("PRAGMA busy_timeout=10000")

        try:
            yield self.local.connection
        except Exception as e:
            self.local.connection.rollback()
            raise e


db = DatabaseManager()
