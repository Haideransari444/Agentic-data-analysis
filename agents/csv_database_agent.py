"""CSV ingestion/support agent for LangGraph pipeline.

Provides production-ready discovery, validation, cleaning and upload utilities
so that fresh CSV datasets can be synchronized with the configured database
backend (Supabase by default). The implementation intentionally performs
aggressive validation, schema normalization, and observability logging to keep
ETL failures visible inside the multi-agent workflow.
"""
from __future__ import annotations

import glob
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import pandas as pd

from agents.supabase_agent import SupabaseAgent
from llm.llm_client import GeminiClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class CSVIngestionReport:
    path: str
    table_name: str
    rows_uploaded: int = 0
    columns: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "table_name": self.table_name,
            "rows_uploaded": self.rows_uploaded,
            "columns": self.columns,
            "success": self.success,
            "error": self.error,
        }


class CSVDatabaseAgent:
    """Production-ready CSV ingestion helper used by the LangGraph entry node."""

    SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    def __init__(
        self,
        llm: Optional[GeminiClient] = None,
        supabase_agent: Optional[SupabaseAgent] = None,
        max_preview_rows: int = 5000,
    ) -> None:
        self.llm = llm or GeminiClient()
        self.supabase_agent = supabase_agent or SupabaseAgent()
        self.max_preview_rows = max_preview_rows

    # ------------------------------------------------------------------
    # Discovery / Validation
    # ------------------------------------------------------------------
    def discover_csv_files(self, directory: str) -> List[str]:
        pattern = os.path.join(directory, "**", "*.csv")
        files = sorted(glob.glob(pattern, recursive=True))
        logger.info("CSVDatabaseAgent: discovered %s CSV files under %s", len(files), directory)
        return files

    def validate_csv(self, path: str) -> Tuple[bool, Optional[str], pd.DataFrame]:
        if not os.path.exists(path):
            return False, "file does not exist", pd.DataFrame()

        file_size_mb = os.path.getsize(path) / (1024 * 1024)
        if file_size_mb == 0:
            return False, "file is empty", pd.DataFrame()

        # For validation we load only a preview slice to keep memory predictable.
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                df = pd.read_csv(path, encoding=encoding, nrows=self.max_preview_rows)
                if df.empty:
                    return False, "no rows detected in CSV", df
                if len(df.columns) == 0:
                    return False, "no columns detected", df
                return True, None, df
            except UnicodeDecodeError:
                continue
            except Exception as exc:  # pragma: no cover - best-effort logging
                logger.warning("CSVDatabaseAgent: failed to read %s with %s (%s)", path, encoding, exc)
                continue
        return False, "unable to decode CSV with supported encodings", pd.DataFrame()

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_table_name(filename: str) -> str:
        base = os.path.splitext(os.path.basename(filename))[0]
        candidate = base.strip().lower().replace(" ", "_").replace("-", "_")
        return "csv_" + "".join(ch for ch in candidate if ch.isalnum() or ch == "_")

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        renamed = {
            col: (
                col.strip()
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace("(", "")
                .replace(")", "")
            )
            for col in df.columns
        }
        df = df.rename(columns=renamed)
        return df

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def upload_csv(self, path: str, table_name: Optional[str] = None) -> CSVIngestionReport:
        table = table_name or self._normalize_table_name(path)
        report = CSVIngestionReport(path=path, table_name=table)

        is_valid, error, df_preview = self.validate_csv(path)
        if not is_valid:
            report.success = False
            report.error = error
            logger.error("CSVDatabaseAgent: validation failed for %s (%s)", path, error)
            return report

        df_preview = self._normalize_columns(df_preview)

        try:
            # Delegate heavy lifting to Supabase agent which streams the full file.
            result = self.supabase_agent.upload_csv_to_supabase(path, table)
            report.success = result.get("success", False)
            report.rows_uploaded = result.get("rows_uploaded", 0)
            report.columns = result.get("columns", list(df_preview.columns))
            report.error = result.get("error")
        except Exception as exc:  # pragma: no cover - runtime safety
            report.success = False
            report.error = str(exc)
            logger.exception("CSVDatabaseAgent: upload failed for %s", path)

        return report

    def upload_all_csvs_in_directory(self, directory: str, limit: Optional[int] = None) -> List[Dict]:
        files = self.discover_csv_files(directory)
        if limit:
            files = files[:limit]

        reports: List[CSVIngestionReport] = []
        for path in files:
            reports.append(self.upload_csv(path))

        # Summarize for downstream agents (LLM friendly)
        summary_text = self._summarize_ingestion(reports)
        logger.info("CSVDatabaseAgent: ingestion summary -> %s", summary_text)
        return [r.to_dict() for r in reports]

    # ------------------------------------------------------------------
    # LLM summarization (optional but helps later planning agency)
    # ------------------------------------------------------------------
    def _summarize_ingestion(self, reports: List[CSVIngestionReport]) -> str:
        if not reports:
            return "No CSV files discovered."

        success_count = sum(1 for r in reports if r.success)
        failure_count = len(reports) - success_count
        tops = ", ".join(f"{r.table_name}({r.rows_uploaded})" for r in reports if r.success)

        prompt = f"""
You ingest CSV files before an analysis run. Provide a concise bullet summary in 2 sentences.
- Successful uploads: {success_count}
- Failures: {failure_count}
- Tables loaded: {tops or 'none'}
Respond with operational highlights only.
"""
        try:
            return self.llm.generate(prompt)
        except Exception:  # pragma: no cover - best effort
            return (
                f"CSV ingestion complete. Success={success_count}, Failure={failure_count}, "
                f"Tables={tops or 'none'}."
            )
