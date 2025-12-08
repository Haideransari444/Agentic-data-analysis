# ENV variables, DB configs
# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Choose DB backend: 'sqlite' or 'supabase'
DB_BACKEND = os.getenv("DB_BACKEND", "supabase")

# SQLite config
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/sample.db")

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SCHEMA = os.getenv("SUPABASE_SCHEMA", "public")

# PostgreSQL direct connection (optional - fallback to RPC when missing)
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "")
SUPABASE_DB_PORT = int(os.getenv("SUPABASE_DB_PORT", "5432"))
SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")

# LLM config (Gemini)
LLM_MODEL = os.getenv("LLM_MODEL", "gemini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
