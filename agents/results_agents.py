"""Transforms raw SQL execution outputs into executive-ready insights."""
from __future__ import annotations

import math
from statistics import mean
from typing import Any, Dict, List, Optional

import pandas as pd

from llm.llm_client import GeminiClient


class ResultExplainerAgent:
    def __init__(self, llm: Optional[GeminiClient] = None) -> None:
        self.llm = llm or GeminiClient()

    def explain(self, sql: str, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        if not rows:
            return "Query returned no rows. Verify filters or timeframe."

        dataframe = pd.DataFrame(rows)
        description = self._describe_dataframe(dataframe)
        prompt = f"""
You are an analytics copilot. Translate the findings below into concise
business-friendly insights (<=4 sentences). Include concrete metrics and trends.

SQL: {sql}
Data profile:
{description}
"""
        try:
            return self.llm.generate(prompt).strip()
        except Exception:
            return description

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _describe_dataframe(df: pd.DataFrame) -> str:
        parts: List[str] = []
        parts.append(f"rows={len(df)}, columns={len(df.columns)}")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = [col for col in df.columns if col not in numeric_cols]

        if numeric_cols:
            summary_lines = []
            for col in numeric_cols[:5]:
                col_series = df[col].dropna()
                if col_series.empty:
                    continue
                summary_lines.append(
                    f"{col}: mean={col_series.mean():.2f}, p50={col_series.median():.2f}, p90={col_series.quantile(0.9):.2f}"
                )
            parts.append("Numeric summary -> " + "; ".join(summary_lines))

        if categorical_cols:
            cat_lines = []
            for col in categorical_cols[:3]:
                top = df[col].value_counts().head(3)
                formatted = ", ".join(f"{idx}:{val}" for idx, val in top.items())
                cat_lines.append(f"{col}: {formatted}")
            parts.append("Categorical hotspots -> " + "; ".join(cat_lines))

        return " | ".join(parts)
