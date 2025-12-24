<!-- GitAds-Verify: J5VZEL78L6VXZWEB6PLXPVHE15BKT5LI -->
 ## GitAds Sponsored
[![Sponsored by GitAds](https://gitads.dev/v1/ad-serve?source=haideransari444/agentic-data-analysis@github)](https://gitads.dev/v1/ad-track?source=haideransari444/agentic-data-analysis@github)


 
 # AI-Powered SQL Analytics Agent

[Getting Started](#getting-started) | [Configuration](#configuration) | [Features](#features)

## What is AI SQL Analytics Agent?

This project is an **autonomous multi-agent system** that transforms natural language into actionable database insights. Rather than making individual LLM calls, this paradigm orchestrates entire analytical workflows through specialized agents working in concert. The system features:

- **Natural Language → SQL Translation**: Ask questions in plain English, get instant results
- **Multi-Agent Architecture**: Specialized agents for generation, execution, analysis, and reporting  
- **Real-Time Dashboards**: Dynamic visualizations that adapt to your data schema
- **Automated PDF Reports**: Chain-of-thought reasoning generates McKinsey-grade executive summaries
- **Full-Stack Integration**: FastAPI backend + Next.js 16 frontend with TypeScript


## Why Multi-Agent Architecture?

1. **LLMs excel at orchestration**: They understand context, reason about workflows, and generate precise outputs. The multi-agent pattern lets them do what they do best - coordinate complex processes rather than just answering single questions.

2. **Token efficiency**: Traditional approaches send massive context windows for each query. This system processes data locally in specialized agents, only sending final outputs to the LLM. Result: 85-90% token reduction.

3. **Handles complex analytics**: When working with large datasets, time series data, or scenarios requiring data processing, filtering, aggregating, and visualizing - a multi-agent system excels by delegating tasks before returning insights.

## How It Works

This project implements the agentic pattern using **LangGraph** for orchestration and **Google Gemini 2.0** for intelligence:

```
User Natural Language Query
            │
            ▼
    ┌───────────────┐
    │ ORCHESTRATOR  │ ◄─── LangGraph Workflow Coordinator
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ CHAIN OF      │ ◄─── Planning & Strategy
    │ THOUGHT AGENT │      • Breaks down query
    └───────┬───────┘      • Plans execution steps
            │              • Determines approach
            ▼
    ┌───────────────────────────────┐
    │     SQL GENERATION LAYER      │
    ├───────────────┬───────────────┤
    │ SQL Generator │ SQL Executor  │ ◄─── Query Creation & Execution
    │ • Analyzes    │ • Runs query  │      • Translates NL to SQL
    │   schema      │ • Handles     │      • Executes against DB
    │ • Generates   │   errors      │      • Returns results
    │   SQL         │ • Processes   │
    │               │   data        │
    └───────┬───────┴───────┬───────┘
            │               │
            ▼               ▼
┌───────────────────────────────────────────────────────────────┐
│         PARALLEL PROCESSING LAYER (8 Agents)                  │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │INSIGHT   │  │VISUAL    │  │ANALYTIC  │  │ANOMALY   │       │ ◄─── Analysis
│  │Pattern   │  │Charts    │  │Stats     │  │Outliers  │       │      & Detection
│  │Detection │  │& Graphs  │  │& Metrics │  │& Errors  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐      │
│  │SUMMARY   │  │METRICS   │  │CORRELAT  │  │TRENDS     │      │ ◄─── Synthesis
│  │Aggregator│  │KPIs      │  │Relations │  │Time Series│      │      & Forecasting
│  │Synthesis │  │Tracking  │  │Analysis  │  │Prediction │      │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘      │
└──────────────────────────────┬────────────────────────────────┘
                               │
                       ▼
            ┌──────────────────┐
            │  INSIGHTS AGENT  │ ◄─── Result Compilation
            │  • Synthesizes   │      • Generates recommendations
            │    findings      │      • Creates executive summary
            │  • Builds report │      • Formats visualizations
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  PDF GENERATOR   │ ◄─── Report Creation
            │  • ReportLab     │      • McKinsey-style formatting
            │  • Charts        │      • Professional layout
            │  • Tables        │      • Data-driven content
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │   SUPABASE DB    │ ◄─── Data Source
            │   PostgreSQL     │      • 2,823 records
            │   REST API       │      • 27 columns
            │   + Pandas       │      • Sales data
            └──────────────────┘
```

**Workflow Execution:**
1. User submits natural language query
2. Orchestrator validates and routes request  
3. Chain of Thought agent plans approach
4. SQL Generator creates optimized queries
5. SQL Executor runs against Supabase
6. 8 processing agents analyze in parallel
7. Insights agent compiles findings
8. PDF Generator creates report
9. Results delivered to user

**Total: 13 Specialized Agents** working in concert

## Screenshots

### Dashboard Overview
![Dashboard](images/WhatsApp%20Image%202025-12-08%20at%2011.45.29%20PM.jpeg)
*Real-time KPI cards and interactive visualizations*

### Natural Language Chat Interface  
![Chat Interface](images/WhatsApp%20Image%202025-12-08%20at%2011.45.40%20PM.jpeg)
*Ask questions naturally - "Show me top 5 countries by sales"*

### AI-Powered Analysis
![Analysis](images/WhatsApp%20Image%202025-12-08%20at%2011.47.21%20PM.jpeg)
*Chain-of-thought reasoning with data-driven insights*

### Dynamic Visualizations
![Charts](images/WhatsApp%20Image%202025-12-08%20at%2011.48.14%20PM.jpeg)
*Automatically generated charts: Bar, Line, Pie, and Geographic*

### Data Explorer
![Explorer](images/WhatsApp%20Image%202025-12-08%20at%2011.48.36%20PM.jpeg)
*Browse database schema and sample data*

### Automated Reports
![Reports](images/WhatsApp%20Image%202025-12-08%20at%2011.49.21%20PM.jpeg)
*PDF report generation with executive summaries*

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend)
- Supabase account
- Google Gemini API key

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/Haideransari444/Agentic-data-analysis.git
```

**2. Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `.env` with your credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=your-gemini-api-key
DB_PASSWORD=your-database-password
```

**3. Frontend Setup**
```bash
cd ai-data-dashboard
npm install

# Configure frontend environment
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**4. Start Services**

Option 1 - Use the launcher:
```bash
python start_full_stack.py
```

Option 2 - Manual start:
```bash
# Terminal 1 - Backend
python api_server.py

# Terminal 2 - Frontend  
cd ai-data-dashboard
npm run dev
```

**5. Access the Application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Backend: http://localhost:8000

## Configuration

### Environment Variables

**Backend (`.env`)**
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
DB_PASSWORD=your-database-password
DB_HOST=db.your-project.supabase.co
DB_NAME=postgres
DB_USER=postgres
DB_PORT=5432

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key
```

**Frontend (`.env.local`)**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Features

### 🎯 Natural Language Queries
```
You: "What are the top 10 customers by revenue?"
AI: [Generates SQL, executes query, returns formatted results with visualization]
```

### 🤖 Multi-Agent Architecture

**SQL Generator Agent**
- Translates natural language to SQL
- Optimizes queries for performance
- Handles complex joins and aggregations

**Executor Agent**  
- Runs queries against Supabase
- Implements retry logic and error handling
- Falls back to Pandas for complex aggregations

**Analysis Agent**
- Interprets query results
- Adds business context
- Identifies trends and patterns

**Insights Agent**
- Generates actionable recommendations
- Creates executive summaries
- Produces PDF reports

### 📊 Dynamic Dashboards

**KPI Cards**
- Total tables and records
- AI agent status
- Query/report counts

**Interactive Charts**
- Sales by Country (Bar Chart)
- Sales Trend (Line Chart)  
- Product Distribution (Pie Chart)
- City Performance (Horizontal Bar)

All charts automatically adapt to your database schema.

### 📄 PDF Report Generation

Chain-of-thought reasoning produces:
- Executive summary (1 paragraph, CEO-ready)
- Problem identification
- Data findings with visualizations
- Quantified recommendations
- Next steps

Example workflow:
```bash
curl -X POST http://localhost:8000/api/report \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze Q4 sales performance"}'
```

```

### 🗄️ Database Integration

**Supabase PostgreSQL**
- Direct table access via REST API
- Automatic schema detection
- Pandas aggregation fallback for GROUP BY queries

**CSV Upload**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sales_data.csv"
```

## API Endpoints

### Analytics
- `POST /api/chat` - Natural language query interface
- `POST /api/analysis` - Execute SQL analysis
- `GET /api/dashboard/stats` - KPI metrics
- `GET /api/dashboard/charts` - Visualization data

### Database
- `GET /api/tables` - List all tables
- `GET /api/schema` - Database schema
- `POST /api/upload` - Upload CSV files

### Reports
- `POST /api/report` - Generate PDF report
- `GET /api/report/status/{taskId}` - Check report status
- `GET /api/report/download/{filename}` - Download report

### Activity
- `GET /api/activity` - Recent query history

Full API documentation: http://localhost:8000/docs

## Technical Stack

### Backend
- **FastAPI** - High-performance async Python framework
- **LangGraph** - Multi-agent workflow orchestration  
- **Google Gemini 2.0** - Advanced language model
- **Supabase** - PostgreSQL database with REST API
- **Pandas** - Data processing and aggregation
- **ReportLab** - PDF generation

### Frontend
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS 4** - Modern utility-first styling
- **Recharts** - Beautiful data visualizations
- **shadcn/ui** - Premium UI components

## Testing

```bash
# Run backend tests
python -m pytest tests/

# Test chain-of-thought agent
python test_chain_of_thought.py

# Test dashboard charts
python test_dashboard.py

# Test API endpoints
python test_api.py
```

## Use Cases

### Business Intelligence
- Sales performance analysis
- Customer segmentation  
- Revenue forecasting
- Market trend identification

### Data Exploration
- Interactive database browsing
- Ad-hoc query execution
- Schema discovery
- Data quality checks

### Automated Reporting
- Executive dashboards
- Daily/weekly summaries
- Custom PDF reports
- Scheduled analytics

## Project Structure

```
ai-sql-agent/
├── agents/                      # Multi-agent implementations
│   ├── chain_of_thought_agent.py   # Report generation (1,114 lines)
│   ├── supabase_agent.py           # Database operations
│   ├── sql_generator.py            # SQL generation
│   ├── sql_executor.py             # Query execution
│   └── results_agents.py           # Result analysis
├── llm/                        # LLM integration
│   └── llm_client.py              # Gemini client
├── db/                         # Database adapters
│   ├── supabase_db.py             # Supabase connector
│   └── sqlite_db.py               # SQLite fallback
├── ai-data-dashboard/          # Next.js frontend
│   ├── app/                       # Pages and routing
│   ├── components/                # React components
│   ├── lib/                       # API client
│   └── public/                    # Static assets
├── api_server.py               # FastAPI backend
├── graph.py                    # LangGraph workflow
├── data_driven_report.py       # PDF report generator (670 lines)
├── streamlit_app.py            # Streamlit web interface
├── config.py                   # Configuration
└── requirements.txt            # Dependencies
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangGraph** by LangChain for multi-agent orchestration
- **Google Gemini** for powerful language understanding
- **Supabase** for seamless PostgreSQL hosting
- **Vercel** for Next.js framework
- **shadcn/ui** for beautiful components

---

**Built with AI, Python, and TypeScript**

## 🛠️ Technical Architecture

### Chain-of-Thought Pipeline

```python
User Query → LLM Planning → SQL Execution → Statistical Analysis 
           → Visualization → Narrative Generation → PDF Assembly
```

### Key Components

#### 1. **ChainOfThoughtAgent** (`chain_of_thought_agent.py`)
- Autonomous planning with LLM
- Multi-dataset SQL execution
- Statistical analysis (aggregation, comparison, correlation, trends)
- Visualization generation (matplotlib/seaborn)
- Data-driven narrative creation

#### 2. **DataDrivenReportGenerator** (`data_driven_report.py`)
- McKinsey/BCG consulting structure
- Custom ReportLab styles (11 paragraph types)
- Problem identification section
- Duplication validation
- Professional PDF formatting

#### 3. **SupabaseAgent** (`supabase_agent.py`)
- PostgreSQL connection with REST API fallback
- SQL parsing and table name extraction
- Pandas aggregation for GROUP BY queries
- Dynamic schema introspection

## 📊 Report Structure

1. **Executive Summary** (5 sentences, single paragraph)
   - Biggest finding with quantified metrics
   - Business risk/opportunity analysis
   - Primary recommendation with expected impact

2. **Data Overview** (metadata only)
   - Dataset count, record totals
   - Date range and dimensions

3. **Key Metrics Dashboard**
   - Top KPIs in structured table
   - Top performers ranking

4. **Problem Identification**
   - 3 problems with business impact
   - Links to recommendations

5. **Performance Analysis**
   - Geographic breakdown
   - Customer behavior patterns
   - Order economics
   - Time-series trends

6. **Critical Insights** (Exactly 3)
   - What data shows / Why it matters / Implication

7. **Strategic Recommendations** (Exactly 3)
   - Action / Expected Impact / Effort / Owner / Timeline

## 🎨 Visualization Examples

- **Bar Charts**: Gradient colors, value labels, top-15 limiting
- **Pie Charts**: Exploding segments, shadows, percentage labels
- **Line Charts**: Filled area, gradient line, sorted data
- **Scatter Plots**: Color-mapped by value, size variation
- **Box Plots**: Custom colors, median highlighting
- **Heatmaps**: Correlation matrices with annotations

## 📈 Performance

- **Report Generation**: ~2 minutes for complete analysis
- **Data Handling**: Tested with 2,823+ records, 27 columns
- **Visualization**: 2-3 charts per report (enforced minimum)
- **Error Rate**: <1% with 3-layer fallback system

## 🤝 Contributing

Built as part of AI engineering portfolio by Muzammil Haider
- LinkedIn: [Click Here](https://www.linkedin.com/in/muzamil-haider444/)

---

**⭐ Star this repository if you find it useful!**
