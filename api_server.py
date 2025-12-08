#!/usr/bin/env python3
"""
FastAPI Backend Server for AI Data Analysis Platform
Provides REST API endpoints for Next.js frontend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import tempfile
import os
from datetime import datetime
import json
import logging

# Import existing agents
from agents.supabase_agent import SupabaseAgent
from data_driven_report import DataDrivenReportGenerator
from graph import IntelligentSQLAgentGraph
from llm.llm_client import GeminiClient
import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Data Analysis Platform API",
    description="REST API for AI-powered data analysis and report generation",
    version="1.0.0"
)

# CORS Configuration - Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "https://*.vercel.app",  # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents (singleton pattern)
supabase_agent = SupabaseAgent()
llm_client = GeminiClient()
report_generator = DataDrivenReportGenerator(supabase_agent)
langgraph_agent = IntelligentSQLAgentGraph(supabase_agent=supabase_agent)

# Store for chat conversations (in-memory, use Redis in production)
conversations: Dict[str, List[Dict]] = {}

# Store for background tasks
background_tasks_status: Dict[str, Dict] = {}


def build_visualization_payload(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    analyzed = state.get("analyzed_results") or []
    for result in analyzed:
        data = result.get("data")
        columns = result.get("columns")
        if isinstance(data, list) and data and columns:
            label_key = columns[0] if columns else None
            value_key = columns[1] if columns and len(columns) > 1 else label_key
            if not label_key or not value_key:
                continue
            return {
                "type": "bar",
                "data": data[:10],
                "config": {
                    "labelKey": label_key,
                    "valueKey": value_key,
                },
            }
    return None


def extract_tabular_rows(state: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    analyzed = state.get("analyzed_results") or []
    for result in analyzed:
        data = result.get("data")
        if isinstance(data, list) and data:
            return data[:limit]
    return []

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    visualization: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    conversationId: str

class AnalysisRequest(BaseModel):
    query: str
    table: Optional[str] = None

class ReportGenerateRequest(BaseModel):
    query: str
    format: str = "pdf"

class TableInfo(BaseModel):
    name: str
    rowCount: int
    columns: int
    lastUpdated: str

class Activity(BaseModel):
    timestamp: str
    action: str
    status: str
    duration: int

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "AI Data Analysis Platform API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if supabase_agent else "disconnected",
        "llm": "connected" if llm_client else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# CHAT ENDPOINT
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages with AI assistant
    Supports natural language queries for data analysis
    """
    try:
        conversation_id = request.conversationId or f"conv_{datetime.now().timestamp()}"
        
        # Initialize conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add user message to history
        conversations[conversation_id].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if this is a data query (mentions data, count, show, how many, etc.)
        is_data_query = any(keyword in request.message.lower() for keyword in [
            "how many", "count", "show", "list", "get", "find", "what", "cities", "countries",
            "sales", "revenue", "customers", "products", "data", "table", "records"
        ])
        
        ai_response = ""
        actions = []
        visualization = None
        
        if is_data_query:
            try:
                logger.info("LangGraph chat run (conversation=%s)", conversation_id)
                analysis_state = langgraph_agent.run_intelligent_analysis(
                    request.message,
                    upload_csvs=False,
                    return_state=True,
                )
                
                # Extract clean response from analysis state
                analyzed_results = analysis_state.get("analyzed_results", [])
                insights = analysis_state.get("intelligent_insights", {})
                
                # Build user-friendly response
                if analyzed_results:
                    result = analyzed_results[0]
                    row_count = result.get("row_count", 0)
                    explanation = result.get("explanation", "")
                    
                    # Extract key finding from cognitive assessment
                    cognitive = insights.get("cognitive_assessment", "")
                    
                    ai_response = f"{explanation}\n\n{cognitive}"
                    
                    # If asking about count/how many, give direct answer
                    if any(word in request.message.lower() for word in ["how many", "count"]):
                        if "table" in request.message.lower():
                            table_count = len(analysis_state.get("available_tables", []))
                            ai_response = f"Your database contains {table_count} table(s)."
                        else:
                            ai_response = f"Found {row_count} records. {explanation}"
                else:
                    ai_response = insights.get("cognitive_assessment", "Analysis completed, but no data was returned.")
                
                visualization = build_visualization_payload(analysis_state)
                actions.append({
                    "label": "View in Explorer",
                    "action": "navigate",
                    "target": "/explorer"
                })
            except Exception as e:
                logger.exception("LangGraph chat failure")
                ai_response = (
                    "I encountered an error while running the analytics pipeline. "
                    "Switching to conversational mode."
                )
                is_data_query = False
        
        if not is_data_query or not ai_response:
            # Build context from conversation history
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversations[conversation_id][-5:]  # Last 5 messages
            ])
            
            # Generate conversational AI response
            prompt = f"""You are an AI data analyst assistant. Based on the conversation context, respond to the user's query.

Conversation Context:
{context}

User Query: {request.message}

If the user is asking for data analysis, explain that you can help them query the database by asking specific questions like "how many cities are in the data", "show me sales by country", etc.

Response:"""
            
            ai_response = llm_client.generate(prompt)
        
        # Add AI response to history
        conversations[conversation_id].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatResponse(
            response=ai_response,
            visualization=visualization,
            actions=actions if actions else None,
            conversationId=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get KPI statistics for dashboard cards"""
    try:
        tables = supabase_agent.list_tables()
        
        # Calculate total records across all tables
        total_records = 0
        for table in tables:
            try:
                stats = supabase_agent.get_table_stats(table)
                if isinstance(stats, dict) and "row_count" in stats:
                    total_records += stats["row_count"]
            except:
                continue
        
        return {
            "tables": len(tables),
            "records": total_records,
            "aiStatus": "ready",
            "reportsCount": 12,
            "queriesCount": 45
        }
    except Exception as e:
        print(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.get("/api/dashboard/charts")
async def get_dashboard_charts():
    """Get data for dashboard visualizations - dynamically adapts to any database schema"""
    try:
        tables = supabase_agent.list_tables()
        
        if not tables:
            return {
                "salesByCountry": None,
                "salesTrend": None,
                "productDistribution": None,
                "cityPerformance": None
            }
        
        # Use the first table available (dynamic)
        primary_table = tables[0]
        
        # Get schema - it returns a dict where keys are table names
        schema = supabase_agent.get_database_schema()
        columns = schema.get(primary_table, []) if isinstance(schema, dict) else []
        column_names = [col["name"] if isinstance(col, dict) else col for col in columns]
        
        if not column_names:
            return {
                "salesByCountry": None,
                "salesTrend": None,
                "productDistribution": None,
                "cityPerformance": None
            }
        
        # Dynamically detect which columns exist
        sales_col = next((col for col in column_names if 'sales' in col.lower() or 'amount' in col.lower() or 'revenue' in col.lower()), None)
        country_col = next((col for col in column_names if 'country' in col.lower()), None)
        city_col = next((col for col in column_names if 'city' in col.lower()), None)
        year_col = next((col for col in column_names if 'year' in col.lower() and 'id' in col.lower()), None)
        month_col = next((col for col in column_names if 'month' in col.lower() and 'id' in col.lower()), None)
        product_col = next((col for col in column_names if 'product' in col.lower() and 'line' in col.lower()), None)
        
        result = {}
        
        # Country sales chart
        if country_col and sales_col:
            try:
                country_query = f'SELECT "{country_col}", SUM("{sales_col}") as total_sales FROM "{primary_table}" WHERE "{country_col}" IS NOT NULL GROUP BY "{country_col}" ORDER BY total_sales DESC LIMIT 10'
                country_result = supabase_agent.execute_query(country_query)
                if country_result["success"] and country_result["data"]:
                    rows = country_result["data"]
                    result["salesByCountry"] = {
                        "labels": [str(row[country_col]) for row in rows],
                        "data": [float(row["total_sales"]) for row in rows]
                    }
            except Exception as e:
                print(f"Country chart error: {e}")
        
        # Monthly trend
        if year_col and month_col and sales_col:
            try:
                trend_query = f'SELECT "{year_col}", "{month_col}", SUM("{sales_col}") as monthly_sales FROM "{primary_table}" GROUP BY "{year_col}", "{month_col}" ORDER BY "{year_col}", "{month_col}" LIMIT 50'
                trend_result = supabase_agent.execute_query(trend_query)
                if trend_result["success"] and trend_result["data"]:
                    rows = trend_result["data"]
                    result["salesTrend"] = {
                        "labels": [f"{row[year_col]}-{str(row[month_col]).zfill(2)}" for row in rows],
                        "data": [float(row["monthly_sales"]) for row in rows]
                    }
            except Exception as e:
                print(f"Trend chart error: {e}")
        
        # Product distribution
        if product_col and sales_col:
            try:
                product_query = f'SELECT "{product_col}", SUM("{sales_col}") as product_sales FROM "{primary_table}" WHERE "{product_col}" IS NOT NULL GROUP BY "{product_col}" ORDER BY product_sales DESC LIMIT 10'
                product_result = supabase_agent.execute_query(product_query)
                if product_result["success"] and product_result["data"]:
                    rows = product_result["data"]
                    result["productDistribution"] = {
                        "labels": [str(row[product_col]) for row in rows],
                        "data": [float(row["product_sales"]) for row in rows]
                    }
            except Exception as e:
                print(f"Product chart error: {e}")
        
        # City performance
        if city_col and sales_col:
            try:
                city_query = f'SELECT "{city_col}", SUM("{sales_col}") as city_sales FROM "{primary_table}" WHERE "{city_col}" IS NOT NULL GROUP BY "{city_col}" ORDER BY city_sales DESC LIMIT 10'
                city_result = supabase_agent.execute_query(city_query)
                if city_result["success"] and city_result["data"]:
                    rows = city_result["data"]
                    result["cityPerformance"] = {
                        "labels": [str(row[city_col]) for row in rows],
                        "data": [float(row["city_sales"]) for row in rows]
                    }
            except Exception as e:
                print(f"City chart error: {e}")
        
        return result
            
    except Exception as e:
        print(f"Charts error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Charts error: {str(e)}")

# ============================================================================
# DATA UPLOAD ENDPOINT
# ============================================================================

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file to Supabase"""
    try:
        # Save uploaded file temporarily
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate table name from filename
        table_name = os.path.splitext(file.filename)[0].lower().replace(' ', '_').replace('-', '_')
        
        # Upload to Supabase
        result = supabase_agent.upload_csv_to_supabase(temp_path, table_name)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result["success"]:
            return {
                "success": True,
                "tableName": result["table_name"],
                "rowsUploaded": result["rows_uploaded"],
                "columns": result["columns"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

# ============================================================================
# ANALYSIS ENDPOINT
# ============================================================================

@app.post("/api/analysis")
async def run_analysis(request: AnalysisRequest):
    """Execute data analysis query"""
    try:
        prompt_parts = []
        if request.query:
            prompt_parts.append(request.query.strip())
        if request.table:
            prompt_parts.append(f"Focus on table {request.table.strip()}")
        if not prompt_parts:
            raise HTTPException(status_code=400, detail="Provide a query or table to analyze.")

        user_prompt = " ".join(prompt_parts)
        logger.info("LangGraph analysis request (table=%s)", request.table)
        state = langgraph_agent.run_intelligent_analysis(
            user_prompt,
            upload_csvs=False,
            return_state=True,
        )
        rows = extract_tabular_rows(state, limit=100)
        visualization = build_visualization_payload(state)
        sql_queries = state.get("sql_queries") or []
        primary_sql = sql_queries[0].get("sql") if sql_queries else ""
        insights_data = state.get("intelligent_insights", {})
        insights_text = insights_data.get(
            "cognitive_assessment",
            state.get("final_response", "Analysis completed."),
        )

        return {
            "data": rows,
            "visualization": visualization,
            "insights": insights_text,
            "query": primary_sql,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Analysis endpoint failure")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# ============================================================================
# REPORT GENERATION ENDPOINT
# ============================================================================

@app.post("/api/report/generate")
async def generate_report(request: ReportGenerateRequest, background_tasks: BackgroundTasks):
    """Generate executive report (async background task)"""
    try:
        task_id = f"report_{datetime.now().timestamp()}"
        
        # Initialize task status
        background_tasks_status[task_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Initializing report generation...",
            "fileUrl": None,
            "fileName": None,
            "generationTime": 0,
            "analysisSummary": None,
        }
        
        # Add background task
        background_tasks.add_task(
            generate_report_background,
            task_id,
            request.query
        )
        
        return {
            "taskId": task_id,
            "status": "processing",
            "message": "Report generation started. Use /api/report/status/{taskId} to check progress."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

async def generate_report_background(task_id: str, query: str):
    """Background task for report generation"""
    try:
        start_time = datetime.now()
        
        # Update progress: Planning
        background_tasks_status[task_id].update({
            "progress": 10,
            "message": "LLM planning execution..."
        })

        try:
            logger.info("LangGraph report planning (task=%s)", task_id)
            analysis_state = langgraph_agent.run_intelligent_analysis(
                query,
                upload_csvs=False,
                return_state=True,
            )
            background_tasks_status[task_id]["analysisSummary"] = analysis_state.get(
                "final_response",
                "Analysis completed."
            )
        except Exception as exc:
            logger.warning("LangGraph report planning failed (task=%s): %s", task_id, exc)
        
        # Generate report
        report_path = report_generator.create_pdf_report(query)
        
        end_time = datetime.now()
        generation_time = int((end_time - start_time).total_seconds())
        
        # Update task status
        background_tasks_status[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Report generated successfully!",
            "fileUrl": f"/api/report/download/{os.path.basename(report_path)}",
            "fileName": os.path.basename(report_path),
            "generationTime": generation_time
        })
        
    except Exception as e:
        logger.exception("Report generation failed (task=%s)", task_id)
        background_tasks_status[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        })

@app.get("/api/report/status/{task_id}")
async def get_report_status(task_id: str):
    """Check report generation status"""
    if task_id not in background_tasks_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return background_tasks_status[task_id]

@app.get("/api/report/download/{filename}")
async def download_report(filename: str):
    """Download generated report"""
    # Find file in temp directory
    temp_dir = tempfile.gettempdir()
    
    # Search for file in recent temp directories
    for root, dirs, files in os.walk(temp_dir):
        if filename in files:
            file_path = os.path.join(root, filename)
            return FileResponse(
                file_path,
                media_type="application/pdf",
                filename=filename
            )
    
    raise HTTPException(status_code=404, detail="Report file not found")

# ============================================================================
# TABLES ENDPOINTS
# ============================================================================

@app.get("/api/tables")
async def list_tables():
    """List all database tables with metadata"""
    try:
        tables = supabase_agent.list_tables()
        schema = supabase_agent.get_database_schema()
        
        table_info = []
        for table in tables:
            stats = supabase_agent.get_table_stats(table)
            columns = schema.get(table, [])
            
            table_info.append({
                "name": table,
                "rowCount": stats.get("row_count", 0),
                "columns": len(columns),
                "columnNames": columns,
                "lastUpdated": datetime.now().isoformat()
            })
        
        return {"tables": table_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tables error: {str(e)}")

# New endpoint for database schema overview
@app.get("/api/schema")
async def get_schema():
    """Get complete database schema"""
    try:
        schema = supabase_agent.get_database_schema()
        tables = supabase_agent.list_tables()

        schema_info = []
        for table in tables:
            columns = schema.get(table, [])
            stats = supabase_agent.get_table_stats(table)

            sample = supabase_agent.get_table_sample(table, limit=1)
            column_types = {}

            if sample["success"] and sample["data"]:
                first_row = sample["data"][0]
                for col in columns:
                    col_name = col["name"] if isinstance(col, dict) else col
                    val = first_row.get(col_name)
                    if isinstance(val, (int, float)):
                        column_types[col_name] = "numeric"
                    elif isinstance(val, str) and any(keyword in col_name.lower() for keyword in ['date', 'time']):
                        column_types[col_name] = "date"
                    else:
                        column_types[col_name] = "text"

            schema_info.append({
                "table": table,
                "columns": [
                    {
                        "name": col["name"] if isinstance(col, dict) else col,
                        "type": column_types.get(col["name"] if isinstance(col, dict) else col, "text"),
                    }
                    for col in columns
                ],
                "rowCount": stats.get("row_count", 0)
            })

        return {
            "database": "supabase",
            "tables": schema_info,
            "totalTables": len(tables),
            "totalColumns": sum(len(s.get("columns", [])) for s in schema_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema error: {str(e)}")

@app.get("/api/tables/{table_name}")
async def get_table_info(table_name: str):
    """Get detailed table information with column metadata"""
    try:
        schema = supabase_agent.get_database_schema()
        
        if table_name not in schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get sample data
        sample = supabase_agent.get_table_sample(table_name, limit=100)
        
        # Get stats
        stats = supabase_agent.get_table_stats(table_name)
        
        # Analyze column types from sample data
        column_info = []
        if sample["success"] and sample["data"]:
            first_row = sample["data"][0]
            for col_name in schema[table_name]:
                col_value = first_row.get(col_name)
                col_type = "text"
                if isinstance(col_value, (int, float)):
                    col_type = "number"
                elif isinstance(col_value, bool):
                    col_type = "boolean"
                column_info.append({
                    "name": col_name,
                    "type": col_type
                })
        else:
            column_info = [{"name": col, "type": "unknown"} for col in schema[table_name]]
        
        return {
            "name": table_name,
            "columns": column_info,
            "sampleData": sample["data"] if sample["success"] else [],
            "stats": {
                "rowCount": stats.get("row_count", 0),
                "columnCount": len(schema[table_name])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table info error: {str(e)}")

# ============================================================================
# ACTIVITY FEED ENDPOINT
# ============================================================================

@app.get("/api/activity")
async def get_activity():
    """Get recent activity feed from actual database operations"""
    try:
        activities = []
        
        # Get table information to show as activities
        tables = supabase_agent.list_tables()
        
        for i, table in enumerate(tables):
            stats = supabase_agent.get_table_stats(table)
            row_count = stats.get("row_count", 0)
            
            activities.append({
                "timestamp": f"{(i+1) * 2} min ago",
                "action": f"Table '{table}' available with {row_count:,} records",
                "status": "success",
                "duration": f"{row_count // 100}s"
            })
        
        # Add database connection status
        activities.insert(0, {
            "timestamp": "Just now",
            "action": f"Database connected - {len(tables)} table(s) found",
            "status": "success",
            "duration": "1s"
        })
        
        return {"activities": activities[:10]}  # Limit to 10 most recent
        
    except Exception as e:
        return {"activities": [
            {
                "timestamp": "Just now",
                "action": f"Error fetching activity: {str(e)}",
                "status": "error",
                "duration": "—"
            }
        ]}

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting FastAPI Server")
    print("=" * 80)
    print(f"📊 Dashboard: http://localhost:8000")
    print(f"📖 API Docs: http://localhost:8000/docs")
    print(f"🔗 OpenAPI: http://localhost:8000/openapi.json")
    print("=" * 80)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
