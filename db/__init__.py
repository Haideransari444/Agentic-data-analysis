# db/__init__.py

from config import DB_BACKEND
from db.sqlite_db import SQLiteDB

def get_db():
    if DB_BACKEND == "sqlite":
        return SQLiteDB()
    elif DB_BACKEND == "supabase":
        # Import SupabaseDB only when needed
        from db.supabase_db import SupabaseDB
        return SupabaseDB()
    else:
        raise ValueError(f"Unknown DB_BACKEND: {DB_BACKEND}")
