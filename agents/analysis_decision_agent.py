"""LLM-backed analysis planning agent for the LangGraph workflow."""
from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional

from llm.llm_client import GeminiClient


class AnalysisDecisionAgent:
    """Builds multi-query analysis plans and follow-up decisions."""

    def __init__(self, llm: Optional[GeminiClient] = None) -> None:
        self.llm = llm or GeminiClient()

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------
    def plan_analysis(self, user_request: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_text = self._format_schema(schema)
        prompt = f"""
You are an autonomous analytics planner embedded inside a LangGraph multi-agent
system. Given the database schema and the analyst's request, design a concrete
execution plan with optimized SQL steps.

Requirements:
1. Provide an `analysis_strategy` (human readable summary).
2. Provide `estimated_complexity` as one of [low, medium, high].
3. Provide 2-4 SQL queries. For each include:
   - `query`: valid PostgreSQL
   - `purpose`: intent in <=120 chars
   - `analysis_type`: choose from [exploratory, comparison, trend, anomaly, attribution]
4. Provide `risk_checks`: list of potential pitfalls (missing data, bias, etc.).
5. Respond as strict JSON (no markdown) following this shape:
{{
  "analysis_strategy": "...",
  "estimated_complexity": "medium",
  "sql_queries": [
     {{"query": "SELECT ...", "purpose": "...", "analysis_type": "trend"}}
  ],
  "risk_checks": ["..."]
}}

Database schema:
{schema_text}

User request: "{user_request.strip()}"
"""

        try:
            raw = self.llm.generate(prompt)
            plan = self._safe_json_parse(raw)
            return self._ensure_minimum_plan(plan, user_request, schema)
        except Exception:
            return self._fallback_plan(user_request, schema)

    # ------------------------------------------------------------------
    # Decision making after execution
    # ------------------------------------------------------------------
    def decide_next_analysis_step(
        self,
        analyzed_results: List[Dict[str, Any]],
        user_request: str,
        analysis_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        summary = self._summarize_results(analyzed_results)
        prompt = f"""
You are reviewing executed SQL analyses for a business stakeholder.
Provide:
- `cognitive_assessment`: health of insights so far (<=2 sentences)
- `insights_so_far`: array of bullet strings referencing concrete metrics
- `remaining_questions`: array of recommended follow-up analyses
Respond in strict JSON.

User objective: {user_request}
Original plan: {analysis_plan.get('analysis_strategy', 'n/a')}
Executed insights summary:
{summary}
"""
        try:
            raw = self.llm.generate(prompt)
            data = self._safe_json_parse(raw)
        except Exception:
            data = {}

        return {
            "cognitive_assessment": data.get(
                "cognitive_assessment", "Analysis completed with automated heuristics."
            ),
            "insights_so_far": data.get("insights_so_far", summary.split("; ")),
            "remaining_questions": data.get(
                "remaining_questions",
                ["Validate findings against latest timeframe", "Drill into drivers of top anomalies"],
            ),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _format_schema(schema: Dict[str, Any]) -> str:
        if not schema:
            return "(schema unavailable)"
        lines = []
        for table, columns in schema.items():
            if isinstance(columns, list) and columns and isinstance(columns[0], dict):
                cols = ", ".join(col.get("name", "col") for col in columns)
            elif isinstance(columns, list):
                cols = ", ".join(columns)
            else:
                cols = "unknown"
            lines.append(f"- {table}: {cols}")
        return "\n".join(lines)

    @staticmethod
    def _safe_json_parse(text: str) -> Dict[str, Any]:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return {}

    def _fallback_plan(self, user_request: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        tables = list(schema.keys()) or ["sales_data"]
        table = tables[0]
        columns = schema.get(table) or []
        numeric_col = next((c for c in columns if "amount" in c or "value" in c), columns[0] if columns else "*")
        query = f'SELECT * FROM "{table}" ORDER BY 1 LIMIT 200'
        return {
            "analysis_strategy": f"Baseline exploration of {table} to satisfy '{user_request}'.",
            "estimated_complexity": "medium",
            "sql_queries": [
                {
                    "query": query,
                    "purpose": "Baseline sampling run",
                    "analysis_type": "exploratory",
                },
                {
                    "query": f'SELECT {numeric_col}, COUNT(*) AS freq FROM "{table}" GROUP BY {numeric_col} LIMIT 20',
                    "purpose": "Distribution snapshot",
                    "analysis_type": "comparison",
                },
            ],
            "risk_checks": ["LLM fallback plan generated", "Verify column mappings"],
        }

    def _ensure_minimum_plan(
        self, plan: Dict[str, Any], user_request: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not plan.get("sql_queries"):
            return self._fallback_plan(user_request, schema)
        if plan.get("estimated_complexity") not in {"low", "medium", "high"}:
            plan["estimated_complexity"] = "medium"
        return plan

    @staticmethod
    def _summarize_results(results: List[Dict[str, Any]]) -> str:
        if not results:
            return "No result rows returned."
        sentences = []
        for result in results:
            purpose = result.get("purpose", "analysis")
            row_count = result.get("row_count", len(result.get("data", [])))
            sentences.append(f"{purpose} -> {row_count} rows")
        return "; ".join(sentences) or "Results captured"
