#!/usr/bin/env python3
"""Simplified Supabase agent using REST API only (no RPC sql function required)"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

import pandas as pd
from supabase import Client, create_client

from config import SUPABASE_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SupabaseAgent:
    """Simplified Supabase integration using REST API only"""
    
    # Known tables in your database - update this list based on your schema
    KNOWN_TABLES = ["sales_data"]  # Add your table names here
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("SupabaseAgent: Connected to Supabase (REST API mode)")
    
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
        """Execute SQL queries - uses RPC for complex queries, REST for simple ones"""
        import re
        
        sql_clean = (sql or "").strip()
        result = self._result_template()

        if not sql_clean:
            result["error"] = "Empty SQL"
            return result

        # Check if this is an aggregation query (GROUP BY, SUM, COUNT, etc.)
        has_aggregation = bool(re.search(r'\b(GROUP\s+BY|SUM|COUNT|AVG|MAX|MIN)\b', sql_clean, re.IGNORECASE))
        
        if has_aggregation:
            # Try to use direct PostgreSQL connection via RPC
            try:
                response = self.supabase.rpc('exec_sql', {'query': sql_clean}).execute()
                rows = response.data or []
                
                result.update({
                    "success": True,
                    "data": rows,
                    "columns": list(rows[0].keys()) if rows else [],
                    "row_count": len(rows),
                })
                return result
            except Exception as rpc_error:
                logger.warning(f"RPC exec_sql failed: {rpc_error}, falling back to pandas aggregation")
                # Fall back to manual aggregation using pandas
                return self._execute_aggregation_with_pandas(sql_clean)
        
        # For simple queries, use REST API
        table_match = re.search(r'FROM\s+["\']?(\w+)["\']?', sql_clean, re.IGNORECASE)
        if not table_match:
            result["error"] = "Could not parse table name from SQL"
            return result
        
        table_name = table_match.group(1)
        
        try:
            # Build query
            query = self.supabase.table(table_name).select("*")
            
            # Parse LIMIT
            limit_match = re.search(r'LIMIT\s+(\d+)', sql_clean, re.IGNORECASE)
            if limit_match:
                query = query.limit(int(limit_match.group(1)))
            else:
                query = query.limit(1000)  # Default limit
            
            # Execute
            response = query.execute()
            rows = response.data or []
            
            result.update({
                "success": True,
                "data": rows,
                "columns": list(rows[0].keys()) if rows else [],
                "row_count": len(rows),
            })
            
        except Exception as exc:
            result["error"] = str(exc)
            logger.error("SupabaseAgent: Query failed (%s)", exc)

        return result
    
    def _execute_aggregation_with_pandas(self, sql: str) -> Dict[str, Any]:
        """Execute aggregation queries using pandas when RPC is not available"""
        import re
        result = self._result_template()
        
        try:
            # Extract table name
            table_match = re.search(r'FROM\s+["\']?(\w+)["\']?', sql, re.IGNORECASE)
            if not table_match:
                result["error"] = "Could not parse table name"
                return result
            
            table_name = table_match.group(1)
            
            # Fetch data from table (limit to 5000 for performance)
            response = self.supabase.table(table_name).select("*").limit(5000).execute()
            if not response.data:
                result["message"] = "No data in table"
                result["success"] = True
                return result
            
            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            
            # Parse GROUP BY columns
            group_by_match = re.search(r'GROUP\s+BY\s+["\']?(\w+)["\']?(?:\s*,\s*["\']?(\w+)["\']?)?', sql, re.IGNORECASE)
            if not group_by_match:
                result["error"] = "Could not parse GROUP BY"
                return result
            
            group_cols = [g for g in group_by_match.groups() if g]
            
            # Parse aggregation (SUM, COUNT, etc.)
            agg_match = re.search(r'(SUM|COUNT|AVG|MAX|MIN)\s*\(\s*["\']?(\w+)["\']?\s*\)\s+as\s+(\w+)', sql, re.IGNORECASE)
            if not agg_match:
                result["error"] = "Could not parse aggregation"
                return result
            
            agg_func = agg_match.group(1).lower()
            agg_col = agg_match.group(2)
            agg_alias = agg_match.group(3)
            
            # Filter WHERE clauses (simple IS NOT NULL)
            where_match = re.search(r'WHERE\s+["\']?(\w+)["\']?\s+IS\s+NOT\s+NULL', sql, re.IGNORECASE)
            if where_match:
                filter_col = where_match.group(1)
                df = df[df[filter_col].notna()]
            
            # Perform aggregation
            if agg_func == 'sum':
                grouped = df.groupby(group_cols)[agg_col].sum().reset_index()
            elif agg_func == 'count':
                grouped = df.groupby(group_cols)[agg_col].count().reset_index()
            elif agg_func == 'avg':
                grouped = df.groupby(group_cols)[agg_col].mean().reset_index()
            elif agg_func == 'max':
                grouped = df.groupby(group_cols)[agg_col].max().reset_index()
            elif agg_func == 'min':
                grouped = df.groupby(group_cols)[agg_col].min().reset_index()
            else:
                result["error"] = f"Unsupported aggregation: {agg_func}"
                return result
            
            grouped.rename(columns={agg_col: agg_alias}, inplace=True)
            
            # Parse ORDER BY
            order_match = re.search(r'ORDER\s+BY\s+(\w+)\s+(ASC|DESC)?', sql, re.IGNORECASE)
            if order_match:
                order_col = order_match.group(1)
                order_dir = (order_match.group(2) or 'ASC').upper() == 'DESC'
                grouped = grouped.sort_values(by=order_col, ascending=not order_dir)
            
            # Parse LIMIT
            limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
            if limit_match:
                grouped = grouped.head(int(limit_match.group(1)))
            
            # Convert to dict records
            rows = grouped.to_dict('records')
            
            result.update({
                "success": True,
                "data": rows,
                "columns": list(grouped.columns),
                "row_count": len(rows),
            })
            
        except Exception as exc:
            result["error"] = f"Pandas aggregation failed: {str(exc)}"
            logger.error("Pandas aggregation error: %s", exc)
        
        return result
    
    def get_database_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """Get schema by sampling first row of each table"""
        schema = {}
        
        for table in self.KNOWN_TABLES:
            try:
                response = self.supabase.table(table).select("*").limit(1).execute()
                if response.data and len(response.data) > 0:
                    first_row = response.data[0]
                    columns = []
                    for col_name, value in first_row.items():
                        col_type = "text"
                        if isinstance(value, (int, float)):
                            col_type = "numeric"
                        elif isinstance(value, bool):
                            col_type = "boolean"
                        columns.append({"name": col_name, "type": col_type, "nullable": True})
                    schema[table] = columns
                    logger.info(f"  ✓ {table}: {[c['name'] for c in columns]}")
            except Exception as e:
                logger.warning(f"  ⚠ Failed to get schema for {table}: {e}")
        
        return schema
    
    def get_table_sample(self, table_name: str, limit: int = 5) -> Dict:
        """Get sample data from a table"""
        try:
            response = self.supabase.table(table_name).select("*").limit(limit).execute()
            return {
                "success": True,
                "data": response.data or [],
                "columns": list(response.data[0].keys()) if response.data else []
            }
        except Exception as e:
            return {"success": False, "error": str(e), "data": [], "columns": []}
    
    def get_table_stats(self, table_name: str) -> Dict:
        """Get basic statistics for a table"""
        try:
            # Get count - Supabase returns count in headers
            response = self.supabase.table(table_name).select("*", count="exact").limit(1).execute()
            return {"row_count": response.count or 0}
        except Exception as e:
            return {"row_count": 0, "error": str(e)}
    
    def list_tables(self) -> List[str]:
        """List all known tables"""
        return self.KNOWN_TABLES.copy()
    
    def upload_csv_to_supabase(self, csv_path: str, table_name: str = None) -> Dict:
        """Upload CSV to Supabase"""
        print(f"📤 Uploading CSV to Supabase: {csv_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            df = self._prepare_dataframe_for_supabase(df, table_name)
            
            if not table_name:
                import os
                table_name = os.path.splitext(os.path.basename(csv_path))[0].lower().replace(' ', '_')
            
            print(f"📊 Uploading {len(df)} rows to table '{table_name}'")
            
            # Convert to records and upload in batches
            records = df.to_dict('records')
            batch_size = 1000
            uploaded = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                try:
                    self.supabase.table(table_name).insert(batch).execute()
                    uploaded += len(batch)
                    print(f"📈 Uploaded {uploaded}/{len(records)} rows")
                except Exception as e:
                    print(f"❌ Batch upload error: {e}")
                    continue
            
            print(f"✅ Successfully uploaded {uploaded} rows to '{table_name}'")
            
            # Update KNOWN_TABLES
            if table_name not in self.KNOWN_TABLES:
                self.KNOWN_TABLES.append(table_name)
            
            return {
                "success": True,
                "table_name": table_name,
                "rows_uploaded": uploaded,
                "columns": list(df.columns),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _prepare_dataframe_for_supabase(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean DataFrame for Supabase"""
        # Clean column names
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
        
        # Handle nulls
        df = df.where(pd.notnull(df), None)
        
        # Convert timestamps to strings
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(5)
                if not sample.empty:
                    first_val = sample.iloc[0]
                    if hasattr(first_val, 'strftime'):
                        df[col] = df[col].astype(str)
        
        return df
