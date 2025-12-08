#!/usr/bin/env python3
"""
Streamlit UI for AI Data Analysis Platform
Modern, clean interface for Supabase integration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from agents.supabase_agent import SupabaseAgent
from graph import IntelligentSQLAgentGraph
from data_driven_report import DataDrivenReportGenerator
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'supabase_agent' not in st.session_state:
    try:
        st.session_state.supabase_agent = SupabaseAgent()
    except Exception as e:
        st.session_state.supabase_agent = None
        st.error(f"❌ Failed to connect to Supabase: {e}")
if 'uploaded_tables' not in st.session_state:
    st.session_state.uploaded_tables = []
if 'sql_agent' not in st.session_state:
    try:
        # Pass the Supabase agent to avoid threading issues
        supabase_agent = st.session_state.get('supabase_agent')
        st.session_state.sql_agent = IntelligentSQLAgentGraph(supabase_agent=supabase_agent)
    except Exception as e:
        st.session_state.sql_agent = None
if 'pdf_generator' not in st.session_state:
    try:
        # Pass the Supabase agent for data access
        supabase_agent = st.session_state.get('supabase_agent')
        st.session_state.pdf_generator = DataDrivenReportGenerator(supabase_agent=supabase_agent)
    except Exception as e:
        st.session_state.pdf_generator = None

def initialize_agents():
    """Initialize all agents"""
    try:
        # All agents are now initialized in session state above
        return st.session_state.supabase_agent is not None
    except Exception as e:
        st.error(f"❌ Initialization failed: {e}")
        return False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 AI Data Analysis Platform</h1>
        <p>Powered by Supabase & LLM Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize agents
    if not initialize_agents():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🚀 Platform Control")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["📊 Dashboard", "📤 Upload Data", "🧠 AI Analysis", "📄 Generate Reports", "🔧 Database Explorer"]
        )
        
        # Database status
        if st.session_state.supabase_agent:
            st.markdown("### 📊 Database Status")
            try:
                tables = st.session_state.supabase_agent.list_tables()
                st.success(f"✅ Connected to Supabase")
                st.info(f"📋 Tables: {len(tables)}")
                
                if tables:
                    st.markdown("**Available Tables:**")
                    for table in tables[:5]:  # Show first 5 tables
                        st.text(f"• {table}")
                    if len(tables) > 5:
                        st.text(f"... and {len(tables) - 5} more")
                        
            except Exception as e:
                st.error(f"❌ Database connection error")
    
    # Main content based on page selection
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📤 Upload Data":
        show_upload_page()
    elif page == "🧠 AI Analysis":
        show_analysis_page()
    elif page == "📄 Generate Reports":
        show_reports_page()
    elif page == "🔧 Database Explorer":
        show_database_explorer()

def show_dashboard():
    """Main dashboard page"""
    st.header("📊 Platform Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🗄️ Tables", len(st.session_state.supabase_agent.list_tables()) if st.session_state.supabase_agent else 0)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Uploads", len(st.session_state.uploaded_tables))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🤖 AI Status", "Ready" if st.session_state.supabase_agent else "Offline")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Platform", "Supabase")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions
    st.header("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload New Data", use_container_width=True):
            st.info("🎉 Data already uploaded! Check the Database Explorer below.")
    
    with col2:
        if st.button("🧠 Run AI Analysis", use_container_width=True):
            st.session_state.page = "🧠 AI Analysis"
            st.rerun()
    
    with col3:
        if st.button("📄 Generate Report", use_container_width=True):
            st.session_state.page = "📄 Reports"
            st.rerun()
    
    # Recent activity
    if st.session_state.uploaded_tables:
        st.header("📈 Recent Uploads")
        df = pd.DataFrame(st.session_state.uploaded_tables)
        st.dataframe(df, use_container_width=True)

def show_upload_page():
    """Data upload page"""
    st.header("📤 Upload Data to Supabase")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your CSV file to analyze with AI"
    )
    
    if uploaded_file:
        # Display file info
        st.info(f"📁 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Preview data
        try:
            preview_df = pd.read_csv(uploaded_file, nrows=5)
            st.subheader("👁️ Data Preview")
            st.dataframe(preview_df, use_container_width=True)
            
            # Upload options
            col1, col2 = st.columns(2)
            
            with col1:
                table_name = st.text_input(
                    "Table Name",
                    value=os.path.splitext(uploaded_file.name)[0].lower().replace(' ', '_'),
                    help="Name for your table in Supabase"
                )
            
            with col2:
                st.write("") # Spacing
                upload_button = st.button(
                    "🚀 Upload to Supabase",
                    type="primary",
                    use_container_width=True
                )
            
            # Upload process
            if upload_button and table_name:
                with st.spinner(f"📤 Uploading {uploaded_file.name} to Supabase..."):
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Upload to Supabase
                    result = st.session_state.supabase_agent.upload_csv_to_supabase(temp_path, table_name)
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    if result["success"]:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Upload Successful!</h4>
                            <p><strong>Table:</strong> {result['table_name']}</p>
                            <p><strong>Rows:</strong> {result['rows_uploaded']:,}</p>
                            <p><strong>Columns:</strong> {len(result['columns'])}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add to session state
                        st.session_state.uploaded_tables.append({
                            "table_name": result['table_name'],
                            "rows": result['rows_uploaded'],
                            "columns": len(result['columns']),
                            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        
                        st.balloons()
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            <h4>❌ Upload Failed</h4>
                            <p>{result['error']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

def show_analysis_page():
    """AI Analysis page"""
    st.header("🧠 AI-Powered Data Analysis")
    
    # Select table
    tables = st.session_state.supabase_agent.list_tables()
    
    if not tables:
        st.warning("📭 No tables found. Please upload data first.")
        return
    
    selected_table = st.selectbox("📋 Select Table to Analyze", tables)
    
    if selected_table:
        # Show table info
        col1, col2 = st.columns(2)
        
        with col1:
            stats = st.session_state.supabase_agent.get_table_stats(selected_table)
            if "row_count" in stats:
                st.metric("📊 Total Rows", f"{stats['row_count']:,}")
        
        with col2:
            sample = st.session_state.supabase_agent.get_table_sample(selected_table, 3)
            if sample["success"]:
                st.metric("📋 Columns", len(sample["columns"]))
        
        # Analysis request
        analysis_request = st.text_area(
            "🤖 What would you like to analyze?",
            placeholder="e.g., 'Find sales trends by region and product category'",
            help="Describe your analysis request in natural language"
        )
        
        if st.button("🚀 Run AI Analysis", type="primary"):
            if analysis_request:
                if st.session_state.sql_agent is None:
                    st.error("❌ SQL agent not available. Please refresh the page.")
                    return
                    
                with st.spinner("🧠 AI is analyzing your data..."):
                    try:
                        result = st.session_state.sql_agent.run_intelligent_analysis(
                            f"Analyze {selected_table}: {analysis_request}"
                        )
                        
                        st.subheader("🎯 Analysis Results")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                        return
                    
                    # Show sample visualization
                    if sample["success"] and sample["data"]:
                        st.subheader("📊 Data Visualization")
                        df = pd.DataFrame(sample["data"])
                        
                        # Simple chart based on data types
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) >= 2:
                            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please enter an analysis request")

def show_reports_page():
    """Reports generation page"""
    st.header("📄 Generate Analysis Reports")
    
    tables = st.session_state.supabase_agent.list_tables()
    
    if not tables:
        st.warning("📭 No tables found. Please upload data first.")
        return
    
    # Report configuration
    col1, col2 = st.columns(2)
    
    with col1:
        selected_tables = st.multiselect("📊 Select Tables", tables)
    
    with col2:
        report_type = st.selectbox(
            "📋 Report Type",
            ["Comprehensive Analysis", "Executive Summary", "Technical Report"]
        )
    
    # Report request
    report_request = st.text_area(
        "📝 Report Description",
        placeholder="e.g., 'Generate comprehensive sales analysis with trends and insights'",
        help="Describe what you want in your report - LLM will determine structure and content autonomously"
    )
    
    if st.button("🎯 Generate CEO-Grade Executive Report", type="primary"):
        if report_request and selected_tables:
            if st.session_state.pdf_generator is None:
                st.error("❌ PDF generator not available. Please refresh the page.")
                return
                
            with st.spinner("🎯 Generating CEO-grade executive report... LLM is autonomously planning structure and content..."):
                try:
                    report_file = st.session_state.pdf_generator.create_pdf_report(
                        report_request
                    )
                    
                    st.success(f"✅ CEO-Grade Executive Report Generated: {os.path.basename(report_file)}")
                    st.info("📋 This report was planned and structured entirely by AI for CEO-level presentation")
                    
                    # Offer download
                    with open(report_file, "rb") as f:
                        st.download_button(
                            label="📥 Download CEO Report",
                            data=f.read(),
                            file_name=os.path.basename(report_file),
                            mime="application/pdf"
                        )
                        
                except Exception as e:
                    st.error(f"❌ Report generation failed: {e}")
        else:
            st.warning("Please select tables and enter a report description")

def show_database_explorer():
    """Database explorer page"""
    st.header("🔧 Database Explorer")
    
    tables = st.session_state.supabase_agent.list_tables()
    
    if not tables:
        st.info("📭 No tables found in your Supabase database")
        return
    
    # Table selector
    selected_table = st.selectbox("📋 Select Table", [""] + tables)
    
    if selected_table:
        # Table information
        st.subheader(f"📊 Table: {selected_table}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Table stats
            stats = st.session_state.supabase_agent.get_table_stats(selected_table)
            if "row_count" in stats:
                st.metric("📈 Rows", f"{stats['row_count']:,}")
                st.metric("🔍 Unique Rows", f"{stats.get('unique_rows', 'N/A'):,}")
        
        with col2:
            # Schema info
            schema = st.session_state.supabase_agent.get_database_schema()
            if selected_table in schema:
                st.write("**Columns:**")
                for col in schema[selected_table]:
                    st.text(f"• {col['name']} ({col['type']})")
        
        # Sample data
        st.subheader("👁️ Sample Data")
        sample = st.session_state.supabase_agent.get_table_sample(selected_table, 10)
        
        if sample["success"]:
            df = pd.DataFrame(sample["data"])
            st.dataframe(df, use_container_width=True)
        
        # Custom query
        st.subheader("⚡ Custom SQL Query")
        custom_query = st.text_area(
            "SQL Query",
            value=f"SELECT * FROM {selected_table} LIMIT 10;",
            help="Write your custom SQL query"
        )
        
        if st.button("🚀 Execute Query"):
            if custom_query:
                result = st.session_state.supabase_agent.execute_query(custom_query)
                
                if result["success"]:
                    if "data" in result:
                        st.dataframe(pd.DataFrame(result["data"]), use_container_width=True)
                        st.info(f"📊 {result.get('row_count', 0)} rows returned")
                    else:
                        st.success(result.get("message", "Query executed successfully"))
                else:
                    st.error(f"❌ Query failed: {result['error']}")

if __name__ == "__main__":
    main()