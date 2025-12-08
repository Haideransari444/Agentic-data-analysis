#!/usr/bin/env python3
"""Supabase database agent with production-grade ergonomics."""

from __future__ import annotations

import logging
import re
import uuid
from typing import Any, Dict, List, Optional

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from supabase import Client, create_client

from config import (
    SUPABASE_DB_HOST,
    SUPABASE_DB_NAME,
    SUPABASE_DB_PASSWORD,
    SUPABASE_DB_PORT,
    SUPABASE_DB_USER,
    SUPABASE_KEY,
    SUPABASE_URL,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SupabaseAgent:
    """
    Modern Supabase integration with PostgreSQL optimization
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.db_connection = None
        self.setup_connection()
    
    def setup_connection(self):
        """Setup direct PostgreSQL connection for complex queries"""
        try:
            if not SUPABASE_DB_HOST or not SUPABASE_DB_USER:
                raise ValueError("Supabase DB credentials missing")
            self.db_connection = psycopg2.connect(
                host=SUPABASE_DB_HOST,
                port=SUPABASE_DB_PORT,
                database=SUPABASE_DB_NAME,
                user=SUPABASE_DB_USER,
                password=SUPABASE_DB_PASSWORD,
            )
            logger.info("SupabaseAgent: Connected to Postgres at %s:%s", SUPABASE_DB_HOST, SUPABASE_DB_PORT)
        except Exception as exc:
            self.db_connection = None
            logger.warning("SupabaseAgent: direct Postgres connection unavailable (%s)", exc)
            logger.warning("SupabaseAgent: falling back to HTTP RPC only")
    
    def upload_csv_to_supabase(self, csv_path: str, table_name: str = None) -> Dict:
        """Upload CSV to Supabase with intelligent processing"""
        
        print(f"📤 Uploading CSV to Supabase: {csv_path}")
        
        try:
            # Read CSV with encoding detection
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    print(f"✅ Read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                return {"success": False, "error": "Could not read CSV file"}
            
            # Clean data for Supabase
            df = self._prepare_dataframe_for_supabase(df, table_name)
            
            # Generate table name if not provided
            if not table_name:
                import os
                table_name = os.path.splitext(os.path.basename(csv_path))[0].lower().replace(' ', '_')
            
            print(f"📊 Preparing {len(df)} rows for table '{table_name}'")
            
            # Create table in Supabase
            self._create_supabase_table(table_name, df)
            
            # Upload data in batches
            batch_size = 1000
            total_rows = len(df)
            uploaded_rows = 0
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:i + batch_size]
                batch_data = batch_df.to_dict('records')
                
                try:
                    result = self.supabase.table(table_name).insert(batch_data).execute()
                    uploaded_rows += len(batch_data)
                    print(f"📈 Uploaded batch {i//batch_size + 1}: {uploaded_rows}/{total_rows} rows")
                except Exception as e:
                    print(f"❌ Batch upload error: {e}")
                    continue
            
            print(f"✅ Successfully uploaded {uploaded_rows} rows to Supabase table '{table_name}'")
            
            return {
                "success": True,
                "table_name": table_name,
                "rows_uploaded": uploaded_rows,
                "columns": list(df.columns),
                "supabase_url": f"{SUPABASE_URL}/dashboard/project/tables/{table_name}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _result_template() -> Dict[str, Any]:
        return {
            "success": False,
            "data": [],
            "columns": [],
            "row_count": 0,
            "message": None,
            "error": None,
        }

    def execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL using Postgres when available, falling back to Supabase REST API."""

        sql_clean = (sql or "").strip()
        result = self._result_template()

        if not sql_clean:
            result["error"] = "Empty SQL"
            return result

        # Try direct PostgreSQL first for lowest latency
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute(sql_clean)

                if cursor.description:
                    rows = cursor.fetchall()
                    data = [dict(row) for row in rows]
                    result.update(
                        {
                            "success": True,
                            "data": data,
                            "columns": [col.name for col in cursor.description],
                            "row_count": len(data),
                        }
                    )
                else:
                    self.db_connection.commit()
                    result.update({"success": True, "message": "Statement executed"})
                return result
            except Exception as exc:
                self.db_connection.rollback()
                logger.warning("SupabaseAgent: Postgres query failed (%s)", exc)
                result["message"] = f"Postgres fallback: {exc}"

        # Fallback to parsing SQL and using Supabase REST API
        try:
            # Extract table name from SELECT queries
            table_name = self._extract_table_name(sql_clean)
            if not table_name:
                result["error"] = "Could not parse table name from SQL. Use direct Postgres connection for complex queries."
                return result

            # Simple SELECT * or SELECT columns queries
            if sql_clean.upper().startswith("SELECT"):
                query = self.supabase.table(table_name).select("*")
                
                # Apply basic WHERE filters if present
                where_match = self._parse_simple_where(sql_clean)
                if where_match:
                    for key, value in where_match.items():
                        query = query.eq(key, value)
                
                # Apply LIMIT if present
                limit_match = self._parse_limit(sql_clean)
                if limit_match:
                    query = query.limit(limit_match)
                
                response = query.execute()
                rows = response.data or []
                result.update(
                    {
                        "success": True,
                        "data": rows,
                        "columns": list(rows[0].keys()) if rows else [],
                        "row_count": len(rows),
                    }
                )
            else:
                result["error"] = "Only SELECT queries supported via REST API. Enable Postgres connection for full SQL support."
        except Exception as exc:
            result["error"] = str(exc)
            logger.error("SupabaseAgent: REST API query failed (%s)", exc)

        return result
    
    def get_database_schema(self) -> Dict:
        """Get all tables and columns from Supabase"""
        
        # Prefer direct Postgres connection for schema queries
        if self.db_connection:
            schema_query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
            """
            
            result = self.execute_query(schema_query)

            if result["success"]:
                schema: Dict[str, List[Dict[str, Any]]] = {}
                for row in result["data"]:
                    table = row["table_name"]
                    if table not in schema:
                        schema[table] = []
                    
                    column_info = {
                        "name": row["column_name"],
                        "type": row["data_type"],
                        "nullable": row["is_nullable"] == "YES"
                    }
                    schema[table].append(column_info)
                
                return schema
        
        # Fallback: Return empty or try to list known tables
        logger.warning("SupabaseAgent: Cannot fetch schema without Postgres connection")
        return {table: [] for table in self.list_tables()}
    
    def get_table_sample(self, table_name: str, limit: int = 5) -> Dict:
        """Get sample data from a table"""
        
        query = f'SELECT * FROM "{table_name}" LIMIT {limit};'
        return self.execute_query(query)
    
    def get_table_stats(self, table_name: str) -> Dict:
        """Get basic statistics for a table"""
        
        stats_query = f'SELECT COUNT(*) as row_count FROM "{table_name}";' 
        result = self.execute_query(stats_query)

        if result["success"] and result["data"]:
            return result["data"][0]
        return {"row_count": 0, "error": result.get("error", "stats unavailable")}
    
    def _prepare_dataframe_for_supabase(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Prepare DataFrame for Supabase upload"""
        
        # Clean column names for PostgreSQL
        df.columns = [
            col.strip().lower()
            .replace(' ', '_')
            .replace('-', '_')
            .replace('.', '_')
            .replace('(', '')
            .replace(')', '')
            .replace('/', '_')
            for col in df.columns
        ]
        
        # Add UUID primary key
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        
        # Handle null values
        df = df.where(pd.notnull(df), None)
        
        # Convert datetime columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                    # Convert to string for JSON serialization
                    df[col] = df[col].astype(str)
                except:
                    pass
        
        # Handle any remaining Timestamp objects
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains Timestamp-like objects
                sample_values = df[col].dropna().head(5)
                if not sample_values.empty:
                    first_val = sample_values.iloc[0]
                    if hasattr(first_val, 'strftime') or str(type(first_val)).endswith("Timestamp'>"):
                        df[col] = df[col].astype(str)
        
        return df
    
    def _create_supabase_table(self, table_name: str, df: pd.DataFrame):
        """Create table structure in Supabase"""
        
        # Generate CREATE TABLE statement
        column_definitions = ["id UUID PRIMARY KEY DEFAULT gen_random_uuid()"]
        
        for col in df.columns:
            if col == 'id':
                continue
                
            # Determine PostgreSQL data type
            if df[col].dtype == 'int64':
                col_type = "INTEGER"
            elif df[col].dtype == 'float64':
                col_type = "DECIMAL"
            elif 'date' in col.lower() or 'time' in col.lower():
                col_type = "TIMESTAMP"
            else:
                col_type = "TEXT"
            
            column_definitions.append(f"{col} {col_type}")
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(column_definitions)}
        );
        """
        
        # Execute table creation
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(create_sql)
                self.db_connection.commit()
                print(f"📋 Created table structure for '{table_name}'")
            except Exception as e:
                print(f"⚠️ Table creation warning: {e}")
    
    def list_tables(self) -> List[str]:
        """List all tables in the database using information_schema query"""
        # Use direct Postgres if available
        if self.db_connection:
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
            result = self.execute_query(query)
            if result["success"]:
                return [row["table_name"] for row in result["data"]]

        # Fallback: manually inspect known tables or use Supabase dashboard
        # For now, try to query information_schema via REST (may not work without RPC)
        logger.warning("SupabaseAgent: Cannot list tables without Postgres connection. Returning empty list.")
        return []
    
    def _extract_table_name(self, sql: str) -> Optional[str]:
        """Extract table name from SQL query"""
        import re
        # Match FROM table_name or FROM "table_name"
        match = re.search(r'FROM\s+["\']?(\w+)["\']?', sql, re.IGNORECASE)
        if match:
            return match.group(1)
        # Try INSERT INTO pattern
        match = re.search(r'INSERT\s+INTO\s+["\']?(\w+)["\']?', sql, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _parse_simple_where(self, sql: str) -> Dict[str, Any]:
        """Parse simple WHERE column = 'value' clauses"""
        import re
        where_dict = {}
        # Match WHERE column = value
        matches = re.findall(r'WHERE\s+(\w+)\s*=\s*["\']?([^"\';\s]+)["\']?', sql, re.IGNORECASE)
        for col, val in matches:
            where_dict[col] = val
        return where_dict
    
    def _parse_limit(self, sql: str) -> Optional[int]:
        """Parse LIMIT clause"""
        import re
        match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def close_connection(self):
        """Close database connection"""
        if self.db_connection:
            self.db_connection.close()
            print("🔌 Closed Supabase connection")