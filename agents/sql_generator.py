# agents/sql_generator.py

from llm.llm_client import GeminiClient

class SQLGeneratorAgent:
    def __init__(self, llm_client: GeminiClient):
        self.llm = llm_client

    def generate_sql(self, question: str, schema: dict) -> str:
        """
        Generate SQL query from natural language question and database schema
        """
        # Build prompt for Gemini
        schema_text = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in schema.items()])
        
        # Provide more context about available data
        table_info = ""
        for table, columns in schema.items():
            table_info += f"\n- {table} table contains: {', '.join(columns)}"
        
        prompt = f"""
You are an expert SQL generator. 
Use the database schema below to write a SQL query that answers the user's question.
Return ONLY the SQL query without any formatting, explanation, or markdown code blocks.

Database Schema:
{schema_text}

Available Tables:{table_info}

Important Guidelines:
- If the user asks for "rows" or "data" without specifying a table, consider which table is most relevant to their question
- If they ask about employees, salaries, departments - use the employees table
- If they ask about products, prices, ratings - use the products table  
- If they ask about customers, orders - use the respective tables
- For generic queries like "show data" or "first rows", show data from the largest/most interesting table

User Question: {question}

SQL Query:"""
        sql = self.llm.generate(prompt)
        
        # Clean up the response - remove markdown formatting and extra whitespace
        sql = sql.strip()
        if sql.startswith('```sql'):
            sql = sql[6:]
        if sql.startswith('```'):
            sql = sql[3:]
        if sql.endswith('```'):
            sql = sql[:-3]
        sql = sql.strip()
        
        return sql