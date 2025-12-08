#!/usr/bin/env python3
"""
Chain-of-Thought Report Agent
Heavy planning -> Data extraction -> Analysis -> Report generation
NO TEMPLATES. ONLY REAL DATA.
"""

from llm.llm_client import GeminiClient
from typing import Dict, List, Any
import json
import re
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os

class ChainOfThoughtReportAgent:
    """
    Heavy planning and execution before report generation
    LLM plans -> Executes -> Analyzes -> Generates
    """
    
    def __init__(self, supabase_agent):
        self.supabase_agent = supabase_agent
        self.llm = GeminiClient()
        self.temp_dir = tempfile.mkdtemp()
        
        # Get actual database schema
        self.database_schema = self._get_database_schema()
        print(f"✓ Database schema loaded: {len(self.database_schema)} tables")
        
    def _get_database_schema(self) -> Dict[str, Dict]:
        """Get REAL database schema with sample data"""
        schema = {}
        
        tables = self.supabase_agent.list_tables()
        
        for table in tables:
            try:
                sample_result = self.supabase_agent.execute_query(f'SELECT * FROM "{table}" LIMIT 5')

                if sample_result["success"] and sample_result["data"]:
                    rows = sample_result["data"]
                    columns = list(rows[0].keys())

                    column_types = {}
                    for col in columns:
                        sample_val = rows[0][col]
                        if isinstance(sample_val, (int, float)):
                            column_types[col] = 'numeric'
                        elif isinstance(sample_val, str):
                            column_types[col] = 'text'
                        else:
                            column_types[col] = 'other'

                    schema[table] = {
                        'columns': columns,
                        'column_types': column_types,
                        'sample_data': rows[:3]
                    }

                    print(f"  ✓ {table}: {columns}")

            except Exception as e:
                print(f"  ⚠ Failed to get schema for {table}: {e}")
        
        return schema
    
    def generate_report(self, user_request: str) -> Dict[str, Any]:
        """
        Main pipeline: Heavy planning -> Execution -> Analysis -> Report
        """
        
        print("\n" + "="*80)
        print("🧠 CHAIN-OF-THOUGHT REPORT GENERATION")
        print("="*80)
        print(f"USER REQUEST: {user_request}\n")
        
        # STEP 1: LLM creates detailed execution plan
        print("STEP 1: 🧠 LLM Planning Phase (Chain-of-Thought)")
        print("-"*80)
        execution_plan = self._llm_create_execution_plan(user_request)
        print(f"✓ Plan created:")
        print(f"  - SQL Queries: {len(execution_plan['sql_queries'])}")
        print(f"  - Analysis Tasks: {len(execution_plan['analysis_tasks'])}")
        print(f"  - Visualizations: {len(execution_plan['visualizations'])}")
        print(f"  - Report Sections: {len(execution_plan['report_sections'])}")
        
        # STEP 2: Execute SQL queries to get REAL data
        print("\nSTEP 2: 📊 Data Extraction Phase")
        print("-"*80)
        datasets = self._execute_sql_queries(execution_plan['sql_queries'])
        print(f"✓ Datasets retrieved: {len(datasets)}")
        for dataset_id, df in datasets.items():
            print(f"  - {dataset_id}: {len(df)} rows × {len(df.columns)} columns")
        
        if not datasets:
            raise Exception("❌ NO DATA RETRIEVED! Cannot generate report without data.")
        
        # STEP 3: Perform statistical analysis on REAL data
        print("\nSTEP 3: 🔬 Statistical Analysis Phase")
        print("-"*80)
        analysis_results = self._perform_statistical_analysis(
            datasets, 
            execution_plan['analysis_tasks']
        )
        print(f"✓ Analysis completed: {len(analysis_results)} results")
        for analysis_id, result in analysis_results.items():
            print(f"  - {analysis_id}: {result.get('method', 'N/A')}")
        
        # STEP 4: Generate visualizations from REAL data
        print("\nSTEP 4: 📈 Visualization Generation Phase")
        print("-"*80)
        visualizations = self._generate_visualizations(
            datasets,
            execution_plan['visualizations']
        )
        print(f"✓ Visualizations created: {len(visualizations)}")
        for viz_id, path in visualizations.items():
            print(f"  - {viz_id}: {os.path.basename(path)}")
        
        # STEP 5: LLM generates narrative FROM THE ACTUAL DATA
        print("\nSTEP 5: ✍️  LLM Narrative Generation (Data-Driven)")
        print("-"*80)
        narrative_content = self._llm_generate_data_driven_narrative(
            user_request,
            execution_plan,
            datasets,
            analysis_results
        )
        print(f"✓ Narrative sections: {len(narrative_content)}")
        
        print("\n" + "="*80)
        print("✅ REPORT GENERATION COMPLETE")
        print("="*80 + "\n")
        
        return {
            'title': execution_plan['report_title'],
            'execution_plan': execution_plan,
            'datasets': datasets,
            'analysis_results': analysis_results,
            'visualizations': visualizations,
            'narrative_content': narrative_content
        }
    
    def _llm_create_execution_plan(self, user_request: str) -> Dict[str, Any]:
        """
        LLM creates detailed step-by-step execution plan
        """
        
        # Build schema context
        schema_context = "DATABASE SCHEMA:\n"
        for table, info in self.database_schema.items():
            schema_context += f"\nTable: {table}\n"
            schema_context += f"Columns:\n"
            for col, col_type in info['column_types'].items():
                schema_context += f"  - {col} ({col_type})\n"
            schema_context += f"Sample data: {info['sample_data'][0]}\n"
        
        planning_prompt = f"""You are a professional data analyst planning a comprehensive CEO-level data analysis report.

USER REQUEST: "{user_request}"

{schema_context}

You are creating a report for executives with the following REQUIRED STRUCTURE:

REPORT STRUCTURE REQUIREMENTS:
1. EXECUTIVE SUMMARY - 3-5 sentences highlighting critical findings with actual numbers
2. DATA OVERVIEW - Records analyzed, date ranges, data sources, quality notes
3. KEY FINDINGS - Top 3-5 insights with supporting metrics and business interpretation
4. DETAILED ANALYSIS - Breakdowns by dimensions, statistical summaries, trends, anomalies
5. RECOMMENDATIONS - Prioritized action items with expected impact and timelines
6. LIMITATIONS & NEXT STEPS - Data limitations and follow-up analyses suggested

CREATE A DETAILED EXECUTION PLAN:

1. SQL QUERIES - What data to fetch? Design specific queries that support comprehensive analysis.
   For each query:
   - query_id: "q1", "q2", etc.
   - sql: PostgreSQL SELECT query (use ONLY tables/columns that exist above)
   - purpose: What this query fetches and how it supports the report structure
   - expected_columns: List of columns this will return

2. ANALYSIS TASKS - What statistical analysis to perform for KPIs and insights?
   For each task:
   - analysis_id: "a1", "a2", etc.
   - method: "aggregation", "correlation", "trend_analysis", "comparison", "distribution"
   - dataset: which query_id to use
   - operation: describe what to calculate (e.g., "sum sales by country", "average order value")
   - metric_name: name of the resulting metric

3. VISUALIZATIONS - What charts tell the story? CREATE AT LEAST 2-3 DIFFERENT VISUALIZATIONS!
   For each viz:
   - viz_id: "v1", "v2", "v3", etc.
   - chart_type: "bar", "pie", "line", "scatter", "box", "heatmap"
   - dataset: which query_id
   - x_axis: column name for x-axis
   - y_axis: column name for y-axis (if applicable)
   - title: chart title
   - aggregation: "sum", "count", "mean", "none"
   
   CRITICAL: Always create at least 2 visualizations showing different perspectives of the data!

4. REPORT SECTIONS - How to structure the report?
   For each section:
   - section_id: "s1", "s2", etc.
   - title: section title
   - content: ["visualization:v1", "analysis:a1", "narrative:topic"]
   - key_insight: main point to communicate

5. REPORT TITLE - One compelling title

RESPOND IN JSON FORMAT:
{{
  "report_title": "Your Title",
  "sql_queries": [
    {{
      "query_id": "q1",
      "sql": "SELECT country, SUM(total) as total_sales FROM sales_data GROUP BY country",
      "purpose": "Get sales by country",
      "expected_columns": ["country", "total_sales"]
    }}
  ],
  "analysis_tasks": [
    {{
      "analysis_id": "a1",
      "method": "aggregation",
      "dataset": "q1",
      "operation": "sum total_sales",
      "metric_name": "total_sales_all_countries"
    }}
  ],
  "visualizations": [
    {{
      "viz_id": "v1",
      "chart_type": "bar",
      "dataset": "q1",
      "x_axis": "country",
      "y_axis": "total_sales",
      "title": "Sales by Country",
      "aggregation": "none"
    }}
  ],
  "report_sections": [
    {{
      "section_id": "s1",
      "title": "Performance Analysis",
      "content": ["narrative:performance", "visualization:v1", "visualization:v2"],
      "key_insight": "Geographic and customer performance patterns"
    }},
    {{
      "section_id": "s2",
      "title": "Critical Insights",
      "content": ["narrative:insights"],
      "key_insight": "Top 3 strategic findings from data"
    }},
    {{
      "section_id": "s3",
      "title": "Strategic Recommendations",
      "content": ["narrative:recommendations"],
      "key_insight": "Prioritized action items with expected impact"
    }}
  ]
}}

CRITICAL REPORT STRUCTURE REQUIREMENTS:
- Create sections that match: Performance Analysis, Critical Insights, Recommendations
- Each section should have unique content - NO REPETITION
- Performance Analysis: Include 2-3 visualizations here
- Critical Insights: Focus on 3 unique findings
- Recommendations: 3 specific action items

USE ONLY THE TABLES AND COLUMNS FROM THE SCHEMA ABOVE. BE SPECIFIC."""

        try:
            response = self.llm.generate(planning_prompt)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                
                # Validate plan has required fields
                if not plan.get('sql_queries'):
                    raise Exception("Plan missing SQL queries")
                
                return plan
            else:
                raise Exception("No JSON found in LLM response")
                
        except Exception as e:
            print(f"⚠ LLM planning failed: {e}")
            # Create intelligent fallback based on request
            return self._create_intelligent_fallback_plan(user_request)
    
    def _create_intelligent_fallback_plan(self, user_request: str) -> Dict[str, Any]:
        """Create smart fallback plan based on available data"""
        
        # Use first table
        table = list(self.database_schema.keys())[0]
        schema = self.database_schema[table]
        
        # Find numeric and text columns
        numeric_cols = [col for col, typ in schema['column_types'].items() if typ == 'numeric']
        text_cols = [col for col, typ in schema['column_types'].items() if typ == 'text']
        
        # Detect if request is about countries
        if 'country' in user_request.lower() or 'countries' in user_request.lower():
            if 'country' in text_cols and len(numeric_cols) > 0:
                value_col = numeric_cols[0]
                
                return {
                    "report_title": f"Sales Analysis by Country",
                    "sql_queries": [
                        {
                            "query_id": "q1",
                            "sql": f"SELECT country, SUM({value_col}) as total_{value_col}, COUNT(*) as count, AVG({value_col}) as avg_{value_col} FROM {table} WHERE country IS NOT NULL GROUP BY country ORDER BY total_{value_col} DESC",
                            "purpose": "Aggregate sales by country",
                            "expected_columns": ["country", f"total_{value_col}", "count", f"avg_{value_col}"]
                        }
                    ],
                    "analysis_tasks": [
                        {
                            "analysis_id": "a1",
                            "method": "aggregation",
                            "dataset": "q1",
                            "operation": f"sum total_{value_col}",
                            "metric_name": "total_revenue"
                        },
                        {
                            "analysis_id": "a2",
                            "method": "comparison",
                            "dataset": "q1",
                            "operation": "top 5 countries by revenue",
                            "metric_name": "top_5_countries"
                        }
                    ],
                    "visualizations": [
                        {
                            "viz_id": "v1",
                            "chart_type": "bar",
                            "dataset": "q1",
                            "x_axis": "country",
                            "y_axis": f"total_{value_col}",
                            "title": "Revenue by Country",
                            "aggregation": "none"
                        },
                        {
                            "viz_id": "v2",
                            "chart_type": "pie",
                            "dataset": "q1",
                            "x_axis": "country",
                            "y_axis": f"total_{value_col}",
                            "title": "Revenue Distribution by Country",
                            "aggregation": "none"
                        },
                        {
                            "viz_id": "v3",
                            "chart_type": "bar",
                            "dataset": "q1",
                            "x_axis": "country",
                            "y_axis": "count",
                            "title": "Order Count by Country",
                            "aggregation": "none"
                        }
                    ],
                    "report_sections": [
                        {
                            "section_id": "s1",
                            "title": "Executive Summary",
                            "content": ["narrative:executive_summary"],
                            "key_insight": "Overall geographic performance"
                        },
                        {
                            "section_id": "s2",
                            "title": "Country Performance Analysis",
                            "content": ["visualization:v1", "visualization:v2", "analysis:a1", "analysis:a2"],
                            "key_insight": "Which countries drive revenue"
                        }
                    ]
                }
        
        # Generic fallback
        return {
            "report_title": f"Data Analysis Report",
            "sql_queries": [
                {
                    "query_id": "q1",
                    "sql": f"SELECT * FROM {table} LIMIT 1000",
                    "purpose": "Get dataset",
                    "expected_columns": schema['columns']
                }
            ],
            "analysis_tasks": [],
            "visualizations": [],
            "report_sections": [
                {
                    "section_id": "s1",
                    "title": "Data Overview",
                    "content": ["narrative:data_summary"],
                    "key_insight": "Data analysis"
                }
            ]
        }
    
    def _execute_sql_queries(self, queries: List[Dict]) -> Dict[str, pd.DataFrame]:
        """Execute SQL queries and return DataFrames"""
        
        datasets = {}
        
        for query in queries:
            query_id = query['query_id']
            sql = query['sql']
            
            try:
                print(f"  → Executing {query_id}: {sql[:80]}...")
                result = self.supabase_agent.execute_query(sql)
                
                if result["success"] and result["data"]:
                    df = pd.DataFrame(result["data"])
                    
                    # If this is a GROUP BY query but we got all rows (REST API limitation),
                    # perform the aggregation in pandas
                    if 'GROUP BY' in sql.upper() and len(df) > 100:  # Likely ungrouped
                        print(f"    ℹ Performing aggregation in pandas (REST API fallback)...")
                        df = self._perform_pandas_aggregation(sql, df)
                    
                    datasets[query_id] = df
                    print(f"    ✓ Success: {len(df)} rows")
                else:
                    print(f"    ⚠ No data returned: {result.get('error')}")
                    
            except Exception as e:
                print(f"    ✗ Failed: {e}")
        
        return datasets
    
    def _perform_pandas_aggregation(self, sql: str, df: pd.DataFrame) -> pd.DataFrame:
        """Perform SQL aggregation in pandas when REST API returns ungrouped data"""
        
        try:
            # Parse GROUP BY columns
            sql_upper = sql.upper()
            group_by_pos = sql_upper.find('GROUP BY')
            if group_by_pos == -1:
                return df
            
            after_group_by = sql[group_by_pos+8:].strip()
            # Extract column names before ORDER BY or end
            group_cols_str = after_group_by.split('ORDER BY')[0].strip()
            group_cols = [col.strip() for col in group_cols_str.split(',')]
            
            # Parse SELECT to find aggregations
            select_pos = sql_upper.find('SELECT')
            from_pos = sql_upper.find('FROM')
            select_clause = sql[select_pos+6:from_pos].strip()
            
            # Build aggregation dict
            agg_dict = {}
            result_cols = {}
            
            # Parse each select item
            for item in select_clause.split(','):
                item = item.strip()
                
                if 'SUM(' in item.upper():
                    # Extract: SUM(column) AS alias
                    col_match = re.search(r'SUM\((\w+)\)', item, re.IGNORECASE)
                    alias_match = re.search(r'AS\s+(\w+)', item, re.IGNORECASE)
                    
                    if col_match:
                        col = col_match.group(1)
                        alias = alias_match.group(1) if alias_match else f'sum_{col}'
                        
                        if col in df.columns:
                            agg_dict[col] = 'sum'
                            result_cols[col] = alias
                
                elif 'AVG(' in item.upper():
                    col_match = re.search(r'AVG\((\w+)\)', item, re.IGNORECASE)
                    alias_match = re.search(r'AS\s+(\w+)', item, re.IGNORECASE)
                    
                    if col_match:
                        col = col_match.group(1)
                        alias = alias_match.group(1) if alias_match else f'avg_{col}'
                        
                        if col in df.columns:
                            agg_dict[col] = 'mean'
                            result_cols[col] = alias
                
                elif 'COUNT(' in item.upper():
                    if 'COUNT(*)' in item.upper() or 'COUNT(DISTINCT' in item.upper():
                        alias_match = re.search(r'AS\s+(\w+)', item, re.IGNORECASE)
                        alias = alias_match.group(1) if alias_match else 'count'
                        
                        # Use first column for counting
                        first_col = df.columns[0]
                        agg_dict[first_col] = 'count'
                        result_cols[first_col] = alias
            
            # Perform aggregation
            if agg_dict:
                grouped = df.groupby(group_cols).agg(agg_dict).reset_index()
                
                # Rename columns according to aliases
                rename_map = {}
                for old_col, new_col in result_cols.items():
                    if old_col in grouped.columns:
                        rename_map[old_col] = new_col
                
                if rename_map:
                    grouped = grouped.rename(columns=rename_map)
                
                return grouped
            
        except Exception as e:
            print(f"    ⚠ Pandas aggregation failed: {e}")
        
        return df
    
    def _perform_statistical_analysis(self, datasets: Dict[str, pd.DataFrame], 
                                     analysis_tasks: List[Dict]) -> Dict[str, Dict]:
        """Perform statistical analysis on datasets"""
        
        results = {}
        
        for task in analysis_tasks:
            analysis_id = task['analysis_id']
            method = task['method']
            dataset_id = task['dataset']
            
            if dataset_id not in datasets:
                print(f"  ⚠ {analysis_id}: Dataset {dataset_id} not available")
                continue
            
            df = datasets[dataset_id]
            
            try:
                print(f"  → {analysis_id}: {method} - {task['operation']}")
                
                if method == 'aggregation':
                    # Extract all numeric columns for aggregation
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    
                    for col in numeric_cols:
                        if col.lower() not in ['id', 'ordernumber', 'qtr_id', 'month_id', 'year_id']:
                            col_sum = float(df[col].sum())
                            col_avg = float(df[col].mean())
                            col_max = float(df[col].max())
                            col_min = float(df[col].min())
                            
                            # Create metrics for each numeric column
                            results[f"{analysis_id}_{col}_total"] = {
                                'method': 'aggregation',
                                'metric': f"Total {col.replace('_', ' ').title()}",
                                'value': col_sum,
                                'formatted': f"${col_sum:,.2f}" if 'sales' in col.lower() or 'price' in col.lower() or 'revenue' in col.lower() else f"{col_sum:,.0f}"
                            }
                            
                            results[f"{analysis_id}_{col}_avg"] = {
                                'method': 'aggregation',
                                'metric': f"Average {col.replace('_', ' ').title()}",
                                'value': col_avg,
                                'formatted': f"${col_avg:,.2f}" if 'sales' in col.lower() or 'price' in col.lower() or 'revenue' in col.lower() else f"{col_avg:,.2f}"
                            }
                    
                    # Also calculate row count
                    results[f"{analysis_id}_count"] = {
                        'method': 'aggregation',
                        'metric': 'Total Records',
                        'value': len(df),
                        'formatted': f"{len(df):,}"
                    }
                
                elif method == 'comparison':
                    # Get top N
                    if 'top' in task['operation'].lower():
                        # Extract number
                        n = int(re.search(r'\d+', task['operation']).group())
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            # Sort by first numeric column
                            sort_col = numeric_cols[0]
                            top_n = df.nlargest(n, sort_col)
                            results[analysis_id] = {
                                'method': 'comparison',
                                'metric': task['metric_name'],
                                'value': top_n.to_dict('records')
                            }
                
                elif method == 'correlation':
                    numeric_df = df.select_dtypes(include=[np.number])
                    if len(numeric_df.columns) >= 2:
                        corr_matrix = numeric_df.corr()
                        results[analysis_id] = {
                            'method': 'correlation',
                            'metric': task['metric_name'],
                            'value': corr_matrix.to_dict()
                        }
                
                elif method == 'distribution':
                    # Calculate distribution stats
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        col = numeric_cols[0]
                        results[analysis_id] = {
                            'method': 'distribution',
                            'metric': task['metric_name'],
                            'value': {
                                'mean': float(df[col].mean()),
                                'median': float(df[col].median()),
                                'std': float(df[col].std()),
                                'min': float(df[col].min()),
                                'max': float(df[col].max())
                            }
                        }
                
                print(f"    ✓ Complete")
                
            except Exception as e:
                print(f"    ✗ Failed: {e}")
        
        # Extract general KPIs from all datasets even if no specific analysis tasks
        if not results:
            print(f"  → Extracting general KPIs from datasets...")
            for dataset_id, df in datasets.items():
                # Find numeric columns with 'sales' or 'revenue'
                for col in df.columns:
                    if ('sales' in col.lower() or 'revenue' in col.lower() or 'amount' in col.lower()) and df[col].dtype in ['int64', 'float64']:
                        total_val = float(df[col].sum())
                        avg_val = float(df[col].mean())
                        
                        results[f"total_{col}"] = {
                            'method': 'aggregation',
                            'metric': f"Total {col.replace('_', ' ').title()}",
                            'value': total_val,
                            'formatted': f"${total_val:,.2f}" if 'sales' in col.lower() or 'revenue' in col.lower() else f"{total_val:,.2f}"
                        }
                        
                        results[f"average_{col}"] = {
                            'method': 'aggregation',
                            'metric': f"Average {col.replace('_', ' ').title()}",
                            'value': avg_val,
                            'formatted': f"${avg_val:,.2f}" if 'sales' in col.lower() or 'revenue' in col.lower() else f"{avg_val:,.2f}"
                        }
                
                # Count unique values in categorical columns
                for col in df.columns:
                    if col.lower() in ['country', 'product', 'category', 'customer', 'region'] and df[col].dtype == 'object':
                        unique_count = int(df[col].nunique())
                        results[f"unique_{col}"] = {
                            'method': 'aggregation',
                            'metric': f"Number of {col.replace('_', ' ').title()}s",
                            'value': unique_count,
                            'formatted': f"{unique_count:,}"
                        }
        
        return results
    
    def _generate_visualizations(self, datasets: Dict[str, pd.DataFrame],
                                viz_plans: List[Dict]) -> Dict[str, str]:
        """Generate visualizations from real data"""
        
        visualizations = {}
        
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 7)
        
        for viz in viz_plans:
            viz_id = viz['viz_id']
            dataset_id = viz['dataset']
            
            if dataset_id not in datasets:
                print(f"  ⚠ {viz_id}: Dataset {dataset_id} not available")
                continue
            
            df = datasets[dataset_id]
            chart_type = viz['chart_type']
            
            try:
                print(f"  → Creating {viz_id} ({chart_type}): {viz['title']}")
                
                fig, ax = plt.subplots(figsize=(12, 7))
                
                x_col = viz.get('x_axis')
                y_col = viz.get('y_axis')
                
                if chart_type == 'bar' and x_col and y_col:
                    # Take top 15 for readability
                    plot_data = df.nlargest(15, y_col) if len(df) > 15 else df
                    
                    # Create gradient colors from dark to light
                    n_bars = len(plot_data)
                    bar_colors = plt.cm.Blues(np.linspace(0.5, 0.9, n_bars))
                    
                    bars = ax.bar(range(len(plot_data)), plot_data[y_col], 
                                 color=bar_colors, edgecolor='#1a365d', linewidth=2, alpha=0.9)
                    
                    # Add subtle shadow effect
                    for bar in bars:
                        bar.set_linewidth(2)
                        bar.set_edgecolor('#1a365d')
                    
                    ax.set_xticks(range(len(plot_data)))
                    ax.set_xticklabels(plot_data[x_col], rotation=45, ha='right', 
                                      fontsize=10, fontweight='600')
                    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    
                    # Grid styling
                    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
                    ax.set_axisbelow(True)
                    
                    # Add value labels with better formatting
                    for i, v in enumerate(plot_data[y_col]):
                        ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom', 
                               fontweight='bold', fontsize=9, color='#2d3748')
                    
                    # Style spines
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_linewidth(1.5)
                    ax.spines['bottom'].set_linewidth(1.5)
                
                elif chart_type == 'pie' and x_col and y_col:
                    # Top 8 for pie chart
                    plot_data = df.nlargest(8, y_col)
                    
                    # Professional color palette for pie
                    pie_colors = ['#2c5282', '#3182ce', '#4299e1', '#63b3ed', 
                                 '#90cdf4', '#f6ad55', '#fc8181', '#9f7aea']
                    
                    # Create pie with explosion effect for emphasis
                    explode = [0.05 if i == 0 else 0.02 for i in range(len(plot_data))]
                    
                    wedges, texts, autotexts = ax.pie(
                        plot_data[y_col], 
                        labels=plot_data[x_col],
                        autopct='%1.1f%%',
                        colors=pie_colors[:len(plot_data)],
                        startangle=90,
                        explode=explode,
                        shadow=True,
                        textprops={'fontsize': 10, 'fontweight': 'bold', 'color': '#2d3748'}
                    )
                    
                    # Style percentage text
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(10)
                    
                    ax.axis('equal')
                
                elif chart_type == 'line' and x_col and y_col:
                    # Sort data for line chart
                    data_sorted = df.sort_values(x_col)
                    
                    # Plot line with gradient fill
                    line = ax.plot(data_sorted[x_col], data_sorted[y_col], 
                                  marker='o', linewidth=3.5, markersize=10, 
                                  color='#2c5282', markerfacecolor='#4299e1', 
                                  markeredgewidth=2, markeredgecolor='#2c5282',
                                  alpha=0.9, zorder=3)
                    
                    # Add fill under line
                    ax.fill_between(data_sorted[x_col], data_sorted[y_col], 
                                   alpha=0.2, color='#4299e1', zorder=1)
                    
                    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    
                    # Enhanced grid
                    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
                    ax.set_axisbelow(True)
                    
                    # Style spines
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_linewidth(1.5)
                    ax.spines['bottom'].set_linewidth(1.5)
                    
                    plt.xticks(rotation=45, ha='right', fontsize=10, fontweight='600')
                
                elif chart_type == 'scatter' and x_col and y_col:
                    # Scatter plot with size and color variation
                    scatter = ax.scatter(df[x_col], df[y_col], 
                                       s=150, alpha=0.7, c=df[y_col],
                                       cmap='Blues', edgecolors='#1a365d', linewidth=2)
                    
                    # Add colorbar
                    cbar = plt.colorbar(scatter, ax=ax)
                    cbar.set_label(y_col.replace('_', ' ').title(), fontsize=11, fontweight='bold')
                    
                    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    
                    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
                    ax.set_axisbelow(True)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                
                elif chart_type == 'box' and y_col:
                    # Box plot with colors
                    bp = ax.boxplot([df[y_col].dropna()], widths=0.6, patch_artist=True,
                                   boxprops=dict(facecolor='#4299e1', color='#2c5282', linewidth=2),
                                   whiskerprops=dict(color='#2c5282', linewidth=2),
                                   capprops=dict(color='#2c5282', linewidth=2),
                                   medianprops=dict(color='#e53e3e', linewidth=3),
                                   flierprops=dict(marker='o', markerfacecolor='#fc8181', 
                                                 markersize=8, markeredgecolor='#e53e3e'))
                    
                    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=13, 
                                 fontweight='bold', color='#2d3748', labelpad=10)
                    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
                    ax.set_axisbelow(True)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                
                elif chart_type == 'heatmap':
                    # Correlation heatmap
                    numeric_cols = df.select_dtypes(include=[np.number]).columns[:10]
                    if len(numeric_cols) > 1:
                        corr = df[numeric_cols].corr()
                        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlBu_r',
                                   center=0, square=True, linewidths=1.5,
                                   cbar_kws={'shrink': 0.8},
                                   ax=ax, vmin=-1, vmax=1)
                        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
                        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)
                
                ax.set_title(viz['title'], fontsize=16, fontweight='bold', 
                            pad=20, color='#1a365d', loc='left')
                plt.tight_layout()
                
                # Save
                filepath = os.path.join(self.temp_dir, f"{viz_id}.png")
                plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
                plt.close()
                
                visualizations[viz_id] = filepath
                print(f"    ✓ Saved: {filepath}")
                
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                plt.close()
        
        return visualizations
    
    def _llm_generate_data_driven_narrative(self, user_request: str, plan: Dict,
                                           datasets: Dict[str, pd.DataFrame],
                                           analysis_results: Dict) -> Dict[str, str]:
        """LLM generates narrative FROM ACTUAL DATA (no templates!)"""
        
        narratives = {}
        
        # Build data context with ACTUAL NUMBERS
        data_context = "ACTUAL DATA ANALYSIS RESULTS:\n\n"
        
        for dataset_id, df in datasets.items():
            data_context += f"Dataset {dataset_id}:\n"
            data_context += f"  Rows: {len(df)}\n"
            data_context += f"  Columns: {list(df.columns)}\n"
            
            # Include actual summary statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                data_context += f"  {col}: sum={df[col].sum():,.2f}, mean={df[col].mean():,.2f}, max={df[col].max():,.2f}, min={df[col].min():,.2f}\n"
            
            # Include categorical breakdowns
            text_cols = df.select_dtypes(include=['object']).columns
            for col in text_cols[:2]:  # Limit to first 2 text columns
                value_counts = df[col].value_counts().head(5)
                data_context += f"  {col} breakdown: {value_counts.to_dict()}\n"
            
            data_context += "\n"
        
        # Include analysis results
        data_context += "ANALYSIS RESULTS (KPIs):\n"
        for analysis_id, result in analysis_results.items():
            metric_name = result.get('metric', analysis_id)
            metric_value = result.get('formatted', result.get('value', 'N/A'))
            data_context += f"  {metric_name}: {metric_value}\n"
        
        # Generate Executive Summary - C-Suite Crisp Format (5 lines max)
        exec_prompt = f"""Write a C-suite executive summary in EXACTLY 5 bullet points:

{data_context}

Format (5 bullets ONLY):
• **Total Revenue**: [Total sales figure across all cities]
• **Biggest Problem**: [One critical issue with specific numbers/percentages]
• **Biggest Opportunity**: [One growth area with potential impact]
• **Key Risk**: [One concentration/trend risk with numbers]
• **Recommended Action**: [One immediate action leadership should take]

Rules:
- Each bullet ONE line maximum
- Include specific numbers/percentages in EVERY bullet
- Name specific cities, product lines, or metrics
- Be direct and actionable
- Total length: 5 lines

Example:
• **Total Revenue**: $10.6M across 73 cities (2003-2005)
• **Biggest Problem**: Madrid ($1.2M, 18%) depends 67% on Classic Cars—catastrophic concentration
• **Biggest Opportunity**: Top 5 cities generate 45% of revenue; expanding next 10 could add $2M
• **Key Risk**: 23 cities under $50K each suggest data quality issues or market failure
• **Recommended Action**: Audit Madrid's portfolio diversity and investigate low-performer data accuracy

Write 5-bullet executive summary now:"""

        try:
            exec_summary = self.llm.generate(exec_prompt)
            narratives['executive_summary'] = exec_summary
            print(f"  ✓ Executive summary: {len(exec_summary)} chars")
        except Exception as e:
            print(f"  ⚠ Executive summary failed: {e}")
            narratives['executive_summary'] = "Analysis in progress."
        
        # Generate DATA OVERVIEW - Dataset validation and facts
        total_records = sum(len(df) for df in datasets.values())
        num_datasets = len(datasets)
        data_overview_prompt = f"""List the datasets used in this analysis. Include:

1. Number of datasets analyzed: {num_datasets}
2. Total records across all datasets: {total_records}
3. Key dimensions captured (cities, years, product lines, deal sizes)
4. Date range covered
5. Any missing or incomplete data noticed

{data_context}

Write a factual overview (3-4 sentences). No analysis, just describe what data we have.

Write:"""

        try:
            data_overview = self.llm.generate(data_overview_prompt)
            narratives['data_overview'] = data_overview
            print(f"  ✓ Data overview: {len(data_overview)} chars")
        except Exception as e:
            print(f"  ⚠ Data overview failed: {e}")
            narratives['data_overview'] = ""
        
        # Generate PROBLEM IDENTIFICATION - Data quality and business risks
        problem_prompt = f"""CRITICAL: Review all datasets for data quality issues and business risks.

{data_context}

Detect and document problems in these categories:

1. **Data Aggregation Issues**:
   - Are total sales identical across multiple datasets? (indicates aggregation bug)
   - Do yearly aggregated datasets show higher average sales than city-level data? (misleading KPIs)
   - Does "Total Records" KPI match the sum of all dataset records?

2. **Missing or Incomplete Data**:
   - Are there cities with surprisingly low sales? (potential underreporting)
   - Missing years or product lines for certain cities?
   - Geographic coverage gaps?

3. **Business Concentration Risks**:
   - Over-reliance on single cities, product lines, or deal sizes?
   - Declining trends in key markets?
   - Underutilized opportunities?

For EACH problem you find, explain:
- **What**: Describe the problem with specific numbers
- **Why it matters**: Business impact
- **Risk**: What happens if we ignore this?

Identify at least 3-5 problems. Be thorough and specific.

Write problems now:"""
        
        try:
            problems = self.llm.generate(problem_prompt)
            narratives['problems'] = problems
            print(f"  ✓ Problem identification: {len(problems)} chars")
        except Exception as e:
            print(f"  ⚠ Problem identification failed: {e}")
            narratives['problems'] = ""
        
        # Generate section narratives based on report structure
        for section in plan.get('report_sections', []):
            section_id = section['section_id']
            section_title = section['title']
            
            # Determine content type based on section title
            if 'finding' in section_title.lower() or 'insight' in section_title.lower():
                section_prompt = f"""Identify 3-4 UNIQUE critical insights (ZERO REPETITION from other sections).

{data_context}

For EACH insight, provide:

**Insight #[N]: [Title]**
- **Finding**: [Specific pattern with EXACT numbers, city names, rankings]
  Example: "Madrid ($1.2M) ranks #1 but NYC ($890K, #2) grows 34% YoY while Madrid declines 8%"
- **Numbers**: 
  • Top 5 cities: [Names with $ amounts]
  • Bottom 5 cities: [Names with $ amounts]
  • Growth rates: [Specific % for key cities]
  • Concentration: [% of revenue from top N cities]
- **Chart Reference**: "See Chart [ID]: [Description]"
- **Strategic Implication**: Why this matters to business
- **Recommended Action**: ONE specific, measurable action
  Example: "Reallocate 2 sales reps from Madrid to NYC (est. +$300K revenue)"

Rules:
- NO generic statements like "cities underperform" - NAME THE CITIES
- NO vague percentages - show "45% ($4.8M of $10.6M)"
- Include top/bottom rankings in EVERY insight
- Reference actual chart IDs (v1, v2, v3)
- Each insight MUST be unique (no overlap with other insights or problems section)
- Each insight MUST have a concrete recommended action

Write 3-4 insights now (each with all elements above):"""

            elif 'performance' in section_title.lower() or 'analysis' in section_title.lower():
                section_prompt = f"""Conduct comprehensive performance analysis with MANDATORY rankings and specific city names.

{data_context}

**1. Geographic Performance**
Provide:
- **Total Revenue**: $X.XM across N cities
- **Top 5 Cities**: [Rank. City Name - $Amount (% of total)]
  Example: "1. Madrid - $1.2M (18%), 2. NYC - $890K (13%), 3. Paris - $670K (10%)..."
- **Bottom 5 Cities**: [Same format with city names]
- **Concentration**: "Top 5 cities account for X% ($X.XM of $X.XM total)"
- **Growth Leaders**: "[City] grew X% YoY, [City] declined X%"
- **Chart Reference**: See Chart v1 for city sales distribution

**2. Product Line Analysis**
- **Top Product Lines by City**: "Madrid: 67% Classic Cars ($800K), NYC: 45% Motorcycles ($400K)"
- **Product Concentration Risk**: Which cities depend on single product line?
- **Diversification Opportunity**: Which cities have balanced mix?
- **Chart Reference**: See Chart v3 for product line breakdown

**3. Deal Size Distribution**
- **By City**: "Madrid: 55% Large deals ($660K), Boston: 70% Small deals ($420K)"
- **High-Value vs High-Volume**: Name specific cities in each category
- **Revenue Efficiency**: "Cities with Large deal concentration: [List with %]"

**4. Temporal Trends**
- **YoY Growth Rates**: "[City] +34%, [City] +18%, [City] -8%" (name at least 5 cities)
- **Emerging vs Mature**: Categorize cities with specific criteria
- **Chart Reference**: See Chart v2 for yearly trends

IMPORTANT: If data is limited (e.g., only 5 cities available out of 73), explicitly state:
"Note: Dataset contains N=73 cities, but only 5 provided in results—limiting ranking depth."

Write 4 paragraphs with ALL rankings and city names:"""

            elif 'recommend' in section_title.lower():
                section_prompt = f"""Provide 5-6 strategic recommendations with CONCRETE actions (not vague suggestions).

{data_context}

**Format for EACH recommendation:**

**Recommendation #[N]: [Action Title]**
- **Action**: [Specific, measurable action]
  Example: "Reallocate 2 senior sales reps from Madrid to NYC and Paris by Q1 2026"
  NOT: "Focus on growing key markets"
- **Rationale**: [Link to specific problem/opportunity with numbers]
  Example: "NYC grew 34% YoY ($890K) while Madrid declined 8%—shift resources to growth markets"
- **Expected Impact**: [Quantified outcome]
  Example: "Estimated +$300K revenue in 6 months, reduce Madrid concentration from 18% to 14%"
- **Effort**: Low/Medium/High
- **Owner**: [Specific team/role]
  Example: "VP Sales Operations + Regional Sales Managers"
- **Timeline**: [Specific dates]
  Example: "Q1 2026 (Jan-Mar): Reallocation; Q2 2026: Measurement"
- **Success Metrics**: [Measurable KPIs]
  Example: "NYC sales reach $1.2M by Q2 2026; Madrid <15% of total revenue"

**Categories to address:**
1. **Data Quality**: Fix aggregation bugs, run ETL audit, validate low-performer data
2. **Concentration Risk**: Diversify Madrid portfolio, expand top 10 cities
3. **Growth Opportunities**: Invest in high-growth cities (name specific cities)
4. **Pricing Strategy**: Adjust pricing in underperforming segments
5. **Team Reallocation**: Move sales resources to opportunity markets
6. **Process Improvement**: Implement city performance dashboards, automate reporting

Provide 5-6 prioritized recommendations (ordered by impact/urgency):"""

            else:
                # General section
                section_prompt = f"""Write content for: {section_title}

KEY INSIGHT: {section.get('key_insight', '')}

{data_context}

Write 2-3 paragraphs of professional analysis using ONLY actual data above.
Include specific numbers, trends, and business implications.

Write in prose paragraphs, be specific with numbers and context."""

            try:
                narrative = self.llm.generate(section_prompt)
                narratives[section_id] = narrative
                print(f"  ✓ Section {section_id}: {len(narrative)} chars")
            except Exception as e:
                print(f"  ⚠ Section {section_id} failed: {e}")
                narratives[section_id] = ""
        
        # Generate NEXT STEPS FOR LEADERSHIP - Concluding section
        next_steps_prompt = f"""Write a concluding "WHAT SHOULD LEADERSHIP DO NEXT?" section.

{data_context}

Provide:

**IMMEDIATE PRIORITIES (Next 30 Days)**
1. [Action] - [Owner] - [Expected outcome]
2. [Action] - [Owner] - [Expected outcome]
3. [Action] - [Owner] - [Expected outcome]

**QUARTERLY ROADMAP (Next 90 Days)**
- **Q1 Priorities**: [3 key initiatives with owners]
- **Quick Wins**: [2 low-effort, high-impact actions]
- **Strategic Investments**: [1-2 longer-term initiatives]

**SUCCESS METRICS TO TRACK**
• [Metric 1]: Target [X], Current [Y]
• [Metric 2]: Target [X], Current [Y]
• [Metric 3]: Target [X], Current [Y]

**DECISION REQUIRED**
"Leadership must decide: [Specific decision with 2-3 options and recommendation]"

Example:
**IMMEDIATE PRIORITIES (Next 30 Days)**
1. Audit Madrid product mix diversification - VP Sales - Reduce Classic Cars from 67% to <50%
2. Validate low-performer city data (23 cities <$50K) - Data Analytics - Confirm accuracy by Jan 15
3. Reallocate 2 sales reps to NYC/Paris - Regional Managers - Deploy by Feb 1

Be specific, actionable, and executive-focused.

Write next steps section now:"""        
        
        try:
            next_steps = self.llm.generate(next_steps_prompt)
            narratives['next_steps'] = next_steps
            print(f"  ✓ Next steps: {len(next_steps)} chars")
        except Exception as e:
            print(f"  ⚠ Next steps failed: {e}")
            narratives['next_steps'] = ""
        
        return narratives
