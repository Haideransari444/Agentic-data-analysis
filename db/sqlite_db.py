# SQLite implementation
# db/sqlite_db.py

import sqlite3
from db.base_db import BaseDB
from config import SQLITE_PATH

class SQLiteDB(BaseDB):
    def __init__(self, path=SQLITE_PATH):
        self.path = path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row

    def execute(self, query: str):
        if self.conn is None:
            self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = rows[0].keys() if rows else []
            return {
                "success": True,
                "rows": [dict(r) for r in rows],
                "columns": columns,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "rows": [],
                "columns": [],
                "error": str(e)
            }

    def get_schema(self):
        if self.conn is None:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )
        tables = [row[0] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in cursor.fetchall()]
            schema[table] = cols
        return schema
