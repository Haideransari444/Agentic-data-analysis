import io
import os
from typing import Any, Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient

# Provide placeholder Supabase credentials so SupabaseAgent instantiation succeeds during import.
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

import api_server


class FakeSupabaseAgent:
    def __init__(self) -> None:
        self.last_upload: Dict[str, Any] = {}

    def list_tables(self) -> List[str]:
        return ["sales_data"]

    def get_database_schema(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "sales_data": [
                {"name": "country", "type": "text"},
                {"name": "total_sales", "type": "numeric"},
            ]
        }

    def get_table_stats(self, table: str) -> Dict[str, int]:
        return {"row_count": 25}

    def execute_query(self, sql: str) -> Dict[str, Any]:
        return {
            "success": True,
            "data": [
                {"country": "US", "total_sales": 120},
                {"country": "CA", "total_sales": 80},
            ],
            "columns": ["country", "total_sales"],
            "row_count": 2,
        }

    def get_table_sample(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        return {
            "success": True,
            "data": [{"country": "US", "total_sales": 120}],
            "columns": ["country", "total_sales"],
        }

    def upload_csv_to_supabase(self, csv_path: str, table_name: str) -> Dict[str, Any]:
        self.last_upload = {"path": csv_path, "table_name": table_name}
        return {
            "success": True,
            "table_name": table_name,
            "rows_uploaded": 2,
            "columns": ["city", "sales"],
        }


class FakeLangGraph:
    def __init__(self) -> None:
        self.prompts: List[str] = []

    def run_intelligent_analysis(self, prompt: str, upload_csvs: bool = False, return_state: bool = False):
        self.prompts.append(prompt)
        state = {
            "final_response": "Stub Insights: revenue steady",
            "analyzed_results": [
                {
                    "purpose": "demo",
                    "analysis_type": "exploratory",
                    "data": [
                        {"country": "US", "total_sales": 120},
                        {"country": "CA", "total_sales": 80},
                    ],
                    "columns": ["country", "total_sales"],
                }
            ],
            "sql_queries": [{"sql": "SELECT country, total_sales FROM sales_data"}],
            "intelligent_insights": {"cognitive_assessment": "Healthy trend"},
        }
        return state if return_state else state["final_response"]


@pytest.fixture
def test_app(monkeypatch) -> Tuple[TestClient, FakeSupabaseAgent, FakeLangGraph]:
    fake_supabase = FakeSupabaseAgent()
    fake_langgraph = FakeLangGraph()
    monkeypatch.setattr(api_server, "supabase_agent", fake_supabase)
    monkeypatch.setattr(api_server, "langgraph_agent", fake_langgraph)
    client = TestClient(api_server.app)
    return client, fake_supabase, fake_langgraph


def test_chat_runs_langgraph(test_app):
    client, _, fake_langgraph = test_app
    response = client.post("/api/chat", json={"message": "show revenue", "conversationId": None})
    assert response.status_code == 200
    body = response.json()
    assert "Stub Insights" in body["response"]
    assert fake_langgraph.prompts[-1] == "show revenue"


def test_analysis_endpoint_returns_rows(test_app):
    client, _, _ = test_app
    response = client.post("/api/analysis", json={"query": "find trends"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 2
    assert body["visualization"]["config"]["labelKey"] == "country"


def test_upload_csv_success(test_app):
    client, fake_supabase, _ = test_app
    csv_bytes = io.BytesIO(b"city,sales\nNY,100\nLA,90\n")
    response = client.post(
        "/api/upload",
        files={"file": ("sample.csv", csv_bytes.getvalue(), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert fake_supabase.last_upload["table_name"] == "sample"
