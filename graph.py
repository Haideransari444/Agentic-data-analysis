# LangGraph nodes & edges
# graph.py

from langgraph.graph import StateGraph, END
from agents.sql_generator import SQLGeneratorAgent
from agents.sql_executor import SQLExecutorAgent
from agents.results_agents import ResultExplainerAgent
from agents.analysis_decision_agent import AnalysisDecisionAgent
from agents.csv_database_agent import CSVDatabaseAgent
from llm.llm_client import GeminiClient
from db import get_db
from typing import Dict, Any, Union
import json

class IntelligentSQLAgentGraph:
    def __init__(self, supabase_agent=None):
        # Initialize LLM
        self.llm = GeminiClient()
        
        # Use provided Supabase agent or create new one
        if supabase_agent:
            self.supabase_agent = supabase_agent
        else:
            from agents.supabase_agent import SupabaseAgent
            self.supabase_agent = SupabaseAgent()
        
        # Initialize all agents
        self.generator = SQLGeneratorAgent(self.llm)
        self.executor = SQLExecutorAgent()
        self.explainer = ResultExplainerAgent()
        self.analysis_agent = AnalysisDecisionAgent(self.llm)
        self.csv_agent = CSVDatabaseAgent(llm=self.llm)
        
        # No SQLite database connection - use Supabase instead
        
        # Create LangGraph with state management
        self.graph = StateGraph(dict)
        self.setup_graph()

    def setup_graph(self):
        """Setup the intelligent multi-agent workflow"""
        
        # Add nodes to graph
        self.graph.add_node("csv_integration", self.csv_integration_node)
        self.graph.add_node("analysis_planning", self.analysis_planning_node)
        self.graph.add_node("sql_generation", self.sql_generation_node)
        self.graph.add_node("sql_execution", self.sql_execution_node)
        self.graph.add_node("result_analysis", self.result_analysis_node)
        self.graph.add_node("intelligent_insights", self.intelligent_insights_node)
        
        # Define workflow edges
        self.graph.add_edge("csv_integration", "analysis_planning")
        self.graph.add_edge("analysis_planning", "sql_generation")
        self.graph.add_edge("sql_generation", "sql_execution")
        self.graph.add_edge("sql_execution", "result_analysis")
        self.graph.add_edge("result_analysis", "intelligent_insights")
        self.graph.add_edge("intelligent_insights", END)
        
        # Set entry point
        self.graph.set_entry_point("csv_integration")
        
        # Compile the graph
        self.workflow = self.graph.compile()

    def csv_integration_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Intelligent CSV integration"""
        print("🔄 Step 1: CSV Integration & Database Preparation")
        
        # Check for CSV files and upload if requested
        if state.get("upload_csvs", False):
            csv_results = self.csv_agent.upload_all_csvs_in_directory(".")
            state["csv_upload_results"] = csv_results
            print(f"📊 Uploaded {len(csv_results)} CSV files to database")
        
        # Get updated database schema using Supabase
        try:
            schema = self.supabase_agent.get_database_schema()
            state["database_schema"] = schema
            state["available_tables"] = list(schema.keys()) if schema else ["sales_data"]
        except Exception as e:
            # Fallback to known table
            print(f"⚠️ Schema detection failed: {e}")
            state["database_schema"] = {"sales_data": []}
            state["available_tables"] = ["sales_data"]
        
        print(f"💾 Database contains tables: {state['available_tables']}")
        return state

    def analysis_planning_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Intelligent analysis planning using LLM cognition"""
        print("🧠 Step 2: Intelligent Analysis Planning")
        
        user_request = state["user_request"]
        schema = state["database_schema"]
        
        # Use LLM intelligence to plan analysis
        analysis_plan = self.analysis_agent.plan_analysis(user_request, schema)
        state["analysis_plan"] = analysis_plan
        
        print(f"🎯 Analysis Strategy: {analysis_plan.get('analysis_strategy', 'Intelligent analysis')}")
        print(f"🔍 Complexity: {analysis_plan.get('estimated_complexity', 'medium')}")
        
        return state

    def sql_generation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: SQL generation based on intelligent analysis plan"""
        print("⚡ Step 3: Intelligent SQL Generation")
        
        analysis_plan = state["analysis_plan"]
        schema = state["database_schema"]
        user_request = state["user_request"]
        
        # Generate SQL queries based on analysis plan
        sql_queries = []
        
        if "sql_queries" in analysis_plan:
            for query_plan in analysis_plan["sql_queries"]:
                sql = query_plan.get("query")
                if not sql or sql == "SELECT statement":
                    # Generate SQL using the generator agent
                    sql = self.generator.generate_sql(
                        f"{query_plan.get('purpose', '')}: {user_request}", 
                        schema
                    )
                
                sql_queries.append({
                    "sql": sql,
                    "purpose": query_plan.get("purpose", "Analysis"),
                    "analysis_type": query_plan.get("analysis_type", "exploratory")
                })
        else:
            # Fallback: generate basic SQL
            sql = self.generator.generate_sql(user_request, schema)
            sql_queries.append({
                "sql": sql,
                "purpose": "Primary analysis",
                "analysis_type": "comprehensive"
            })
        
        state["sql_queries"] = sql_queries
        print(f"📝 Generated {len(sql_queries)} intelligent SQL queries")
        
        return state

    def sql_execution_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Execute SQL queries with intelligent error handling using Supabase"""
        print("🔧 Step 4: Intelligent SQL Execution")
        
        sql_queries = state["sql_queries"]
        execution_results = []
        
        for i, query_info in enumerate(sql_queries):
            print(f"   Executing query {i+1}: {query_info['purpose']}")
            
            # Use Supabase agent for execution instead of SQLite
            try:
                result = self.supabase_agent.execute_query(query_info["sql"])
                
                if result["success"]:
                    # Convert to expected format
                    execution_result = {
                        "success": True,
                        "rows": result["data"],
                        "columns": list(result["data"][0].keys()) if result["data"] else [],
                        "purpose": query_info["purpose"],
                        "analysis_type": query_info["analysis_type"],
                        "original_sql": query_info["sql"]
                    }
                    print(f"   ✅ Query success: {len(result['data'])} rows")
                else:
                    execution_result = {
                        "success": False,
                        "error": result["error"],
                        "purpose": query_info["purpose"],
                        "analysis_type": query_info["analysis_type"],
                        "original_sql": query_info["sql"]
                    }
                    print(f"   ❌ Query failed: {result['error']}")
                    
            except Exception as e:
                execution_result = {
                    "success": False,
                    "error": str(e),
                    "purpose": query_info["purpose"],
                    "analysis_type": query_info["analysis_type"],
                    "original_sql": query_info["sql"]
                }
                print(f"   ❌ Query failed: {str(e)}")
            
            execution_results.append(execution_result)
        
        state["execution_results"] = execution_results
        return state

    def result_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Analyze results using intelligent processing"""
        print("📊 Step 5: Intelligent Result Analysis")
        
        execution_results = state["execution_results"]
        analyzed_results = []
        
        for result in execution_results:
            if result["success"]:
                # Use explainer agent to analyze results
                explanation = self.explainer.explain(
                    result["original_sql"], 
                    result["rows"], 
                    result["columns"]
                )
                
                analyzed_result = {
                    "purpose": result["purpose"],
                    "analysis_type": result["analysis_type"],
                    "data": result["rows"],
                    "columns": result["columns"],
                    "explanation": explanation,
                    "row_count": len(result["rows"])
                }
                
                analyzed_results.append(analyzed_result)
        
        state["analyzed_results"] = analyzed_results
        print(f"🎯 Analyzed {len(analyzed_results)} successful queries")
        
        return state

    def intelligent_insights_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Generate intelligent insights using LLM cognition"""
        print("🧠 Step 6: Generating Intelligent Insights")
        
        user_request = state["user_request"]
        analysis_plan = state["analysis_plan"]
        analyzed_results = state["analyzed_results"]
        
        # Use LLM to generate intelligent insights
        insights = self.analysis_agent.decide_next_analysis_step(
            analyzed_results, user_request, analysis_plan
        )
        
        state["intelligent_insights"] = insights
        state["final_response"] = self._compile_final_response(state)
        
        print("✅ Intelligent analysis complete!")
        return state

    def _compile_final_response(self, state: Dict[str, Any]) -> str:
        """Compile comprehensive intelligent response"""
        
        analyzed_results = state.get("analyzed_results", [])
        insights = state.get("intelligent_insights", {})
        analysis_plan = state.get("analysis_plan", {})
        
        response = f"""
🧠 INTELLIGENT DATA ANALYSIS RESULTS

📋 ANALYSIS STRATEGY:
{analysis_plan.get('analysis_strategy', 'Comprehensive intelligent analysis')}

🎯 COGNITIVE ASSESSMENT:
{insights.get('cognitive_assessment', 'Analysis completed successfully')}

📊 DATA FINDINGS:
"""
        
        for i, result in enumerate(analyzed_results, 1):
            response += f"\n{i}. {result['purpose']} ({result['row_count']} rows)\n"
            response += f"   {result['explanation'][:200]}...\n"
        
        response += f"""
💡 INTELLIGENT INSIGHTS:
{json.dumps(insights.get('insights_so_far', ['Advanced pattern analysis completed']), indent=2)}

🚀 NEXT STEPS:
{json.dumps(insights.get('remaining_questions', ['Analysis objectives achieved']), indent=2)}
"""
        
        return response

    def run_intelligent_analysis(
        self,
        user_request: str,
        upload_csvs: bool = False,
        return_state: bool = False,
    ) -> Union[str, Dict[str, Any]]:
        """Run the complete intelligent analysis workflow."""
        
        initial_state = {
            "user_request": user_request,
            "upload_csvs": upload_csvs
        }
        
        try:
            final_state = self.workflow.invoke(initial_state)
            if return_state:
                return final_state
            return final_state.get("final_response", "Analysis completed")
            
        except Exception as e:
            return f"❌ Intelligent analysis failed: {e}"

    def run(self, question: str) -> str:
        """Legacy interface for backward compatibility"""
        return self.run_intelligent_analysis(question, upload_csvs=True)

if __name__ == "__main__":
    # Test the Intelligent SQL Agent
    try:
        agent = IntelligentSQLAgentGraph()
        print("🤖 Intelligent SQL Agent initialized successfully!")
        
        print("\nDatabase Schema:")
        schema = agent.csv_agent.get_database_schema()
        for table, columns in schema.items():
            print(f"  📊 {table}: {', '.join(columns)}")
        
        print("\n" + "="*60)
        print("🧠 Testing Intelligent Analysis...")
        
        # Test intelligent analysis
        test_request = "analyze sales trends and customer patterns"
        result = agent.run_intelligent_analysis(test_request, upload_csvs=True)
        
        print("\n🎯 INTELLIGENT ANALYSIS RESULT:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
