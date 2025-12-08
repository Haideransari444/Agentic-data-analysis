# agents/sql_executor.py

from db import get_db

class SQLExecutorAgent:
    """
    Executes validated SQL queries on the database.
    Works with any DB backend (SQLite or Supabase) via BaseDB interface.
    """

    def __init__(self):
        self.db = get_db()
        self.db.connect()

    def execute(self, sql: str) -> dict:
        """
        Executes the SQL query and returns:
        {
            success: bool,
            rows: list of dict,
            columns: list of str,
            error: str or None
        }
        """
        result = self.db.execute(sql)
        return result
