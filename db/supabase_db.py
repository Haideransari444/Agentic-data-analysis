# db/supabase_db.py

from db.base_db import BaseDB
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SCHEMA
from supabase import create_client, Client

class SupabaseDB(BaseDB):
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def connect(self):
        # Supabase client is ready on init, nothing else required
        pass

    def execute(self, query: str):
        try:
            result = self.client.rpc("sql", {"q": query}).execute()
            rows = result.data if result.data else []
            columns = list(rows[0].keys()) if rows else []
            return {
                "success": True,
                "rows": rows,
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
        """
        Pulls schema info from Supabase information_schema
        Returns dict: {table_name: [column1, column2,...]}
        """
        query = f"""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = '{SUPABASE_SCHEMA}';
        """
        result = self.client.rpc("sql", {"q": query}).execute()
        schema = {}
        for row in result.data:
            table = row["table_name"]
            col = row["column_name"]
            schema.setdefault(table, []).append(col)
        return schema
