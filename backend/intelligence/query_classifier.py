"""
query_classifier.py — Hybrid query classifier (LLM-first, keyword fallback).
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from intelligence.llm_client import understand_query

logger = logging.getLogger("ai_analyst.classifier")

# ─── Keyword Patterns (fallback) ─────────────────────────────────────────────
_INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ("prediction",         ["predict", "forecast", "future", "next", "will", "project", "estimate", "expected"]),
    ("trend",              ["trend", "over time", "time series", "growth", "decline", "change", "monthly", "weekly", "daily", "yearly", "quarterly"]),
    ("feature_importance", ["affect", "impact", "effect", "influence", "important", "driver", "driving", "factor", "contribute"]),
    ("correlation",        ["correlat", "relationship", "relate", "association", "heatmap"]),
    ("comparison",         ["compare", "vs", "versus", "difference", "between", "rank", "top", "bottom", "highest", "lowest", "best", "worst"]),
    ("aggregation",        ["average", "mean", "sum", "total", "max", "maximum", "min", "minimum", "count", "how many", "median", "std"]),
    ("distribution",       ["distribution", "histogram", "spread", "range", "outlier", "skew", "percentile"]),
    ("anomaly",            ["anomaly", "anomalies", "unusual", "outlier", "suspicious", "abnormal", "weird"]),
]


def _keyword_classify(query: str) -> str:
    """Classify query intent using keyword patterns."""
    if not query.strip():
        return "general"
    q = query.lower()
    for intent, keywords in _INTENT_PATTERNS:
        if any(kw in q for kw in keywords):
            return intent
    return "general"


def classify_query(
    query: str,
    columns: list[str],
) -> tuple[str, Optional[dict[str, Any]]]:
    """
    Hybrid classifier:
    1. Try LLM understanding first → get structured JSON + intent
    2. If LLM fails, fall back to keyword classification

    Returns (intent_string, llm_parsed_dict_or_None)
    """
    # ── Try LLM first ─────────────────────────────────────────────────────
    llm_result = understand_query(query, columns)

    if llm_result and llm_result.get("operation"):
        operation = llm_result["operation"].lower().strip()
        # Normalize operation to our intent names
        intent_map = {
            "aggregation": "aggregation",
            "trend": "trend",
            "correlation": "correlation",
            "comparison": "comparison",
            "prediction": "prediction",
            "distribution": "distribution",
            "anomaly": "anomaly",
            "feature_importance": "feature_importance",
            "general": "general",
        }
        intent = intent_map.get(operation, "general")
        logger.info("LLM classified query as '%s'", intent)
        return intent, llm_result

    # ── Fallback to keywords ──────────────────────────────────────────────
    intent = _keyword_classify(query)
    logger.info("Keyword classified query as '%s' (LLM unavailable)", intent)
    return intent, None
