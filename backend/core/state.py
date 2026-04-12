"""
state.py — In-memory application state (singleton).
"""
from __future__ import annotations

from collections import deque
from typing import Any, Optional

import pandas as pd

from core.config import HISTORY_MAX_LEN


class AppState:
    """Thread-local in-memory state for the running application."""

    def __init__(self) -> None:
        self.df: Optional[pd.DataFrame] = None
        self.schema: Any = None
        self.filename: Optional[str] = None
        self.history: deque = deque(maxlen=HISTORY_MAX_LEN)
        # RAG state
        self.rag_index: Any = None
        self.rag_chunks: list[str] = []
        self.rag_doc_name: Optional[str] = None

    def reset_dataset(self) -> None:
        self.df = None
        self.schema = None
        self.filename = None
        self.history.clear()

    def has_dataset(self) -> bool:
        return self.df is not None

    def has_rag(self) -> bool:
        return self.rag_index is not None


# Singleton
app_state = AppState()
