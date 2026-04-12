"""
config.py — Centralized settings for the AI Data Analyst backend.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── Ollama / LLM ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

# ─── File Upload ──────────────────────────────────────────────────────────────
MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS: tuple[str, ...] = (".csv", ".xlsx", ".xls")

# ─── Reports ──────────────────────────────────────────────────────────────────
REPORTS_DIR: Path = Path(tempfile.gettempdir()) / "ai_analyst_reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ─── RAG ──────────────────────────────────────────────────────────────────────
RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))

# ─── History ──────────────────────────────────────────────────────────────────
HISTORY_MAX_LEN: int = 10

# ─── Revenue / Metric Keywords ───────────────────────────────────────────────
# Columns containing these keywords should default to SUM, not MEAN
REVENUE_KEYWORDS: list[str] = [
    "revenue", "sales", "total", "amount", "income", "turnover",
    "earnings", "gross", "net", "profit", "value",
]
