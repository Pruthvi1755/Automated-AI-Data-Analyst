"""
llm_client.py — Ollama LLaMA3 client for query understanding and insight generation.

Two responsibilities:
1. Parse user query → structured JSON (metric, aggregation, group_by, etc.)
2. Generate natural-language insights from computation results.

Graceful fallback: if Ollama is unavailable, returns None so the caller
can fall back to keyword-based classification + template insights.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

import httpx

from core.config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TIMEOUT

logger = logging.getLogger("ai_analyst.llm")

# ─── Prompts ──────────────────────────────────────────────────────────────────

_QUERY_UNDERSTANDING_PROMPT = """You are an expert data analyst AI. Given a user's natural language query and the dataset columns, extract the analytical intent into STRICT JSON.

RULES:
- "highest", "top", "most", "total" → aggregation: "sum"
- "average", "mean", "avg" → aggregation: "mean"
- "trend", "over time", "monthly", "weekly" → operation: "trend"
- "affect", "impact", "influence", "importance", "driver" → operation: "feature_importance"
- "correlat", "relationship", "relate" → operation: "correlation"
- "predict", "forecast", "future" → operation: "prediction"
- "anomal", "outlier", "unusual" → operation: "anomaly"
- "distribut", "histogram", "spread" → operation: "distribution"
- "compare", "vs", "rank", "top", "bottom", "best", "worst" → operation: "comparison"
- For revenue/sales/amount queries, ALWAYS use "sum" unless user explicitly says "average"
- NEVER map revenue to price — they are different concepts

Return ONLY valid JSON, no markdown, no explanation:
{{
  "metric": "<column name or empty string>",
  "aggregation": "<sum|mean|max|min|count|median|std or empty>",
  "group_by": "<column name or empty string>",
  "operation": "<aggregation|trend|correlation|comparison|prediction|distribution|anomaly|feature_importance|general>",
  "filters": [],
  "time_grain": "<day|week|month|quarter|year or empty>"
}}

Dataset columns: {columns}

User query: "{query}"

JSON:"""

_INSIGHT_GENERATION_PROMPT = """You are an expert data analyst. Given the analysis results below, generate 2-3 concise, actionable business insights. Use specific numbers from the results. Be direct and professional.

Analysis type: {intent}
Query: "{query}"
Result: {result}

Write insights as bullet points. Use **bold** for key numbers and entities. Keep each insight to 1-2 sentences max."""


# ─── Client ──────────────────────────────────────────────────────────────────

def _call_ollama(prompt: str, temperature: float = 0.1) -> Optional[str]:
    """Call Ollama API. Returns response text or None on failure."""
    try:
        with httpx.Client(timeout=LLM_TIMEOUT) as client:
            resp = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 512,
                    },
                },
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
    except httpx.ConnectError:
        logger.warning("Ollama not reachable at %s — falling back to keyword classifier", OLLAMA_BASE_URL)
        return None
    except httpx.TimeoutException:
        logger.warning("Ollama request timed out after %ds", LLM_TIMEOUT)
        return None
    except Exception as e:
        logger.warning("Ollama call failed: %s", e)
        return None


def understand_query(query: str, columns: list[str]) -> Optional[dict[str, Any]]:
    """
    Use LLM to parse a user query into structured intent JSON.
    Returns parsed dict or None if LLM is unavailable.
    """
    prompt = _QUERY_UNDERSTANDING_PROMPT.format(
        columns=", ".join(columns),
        query=query,
    )
    raw = _call_ollama(prompt, temperature=0.05)
    if not raw:
        return None

    # Try to extract JSON from the response
    try:
        # Strip markdown code fences if present
        cleaned = re.sub(r"```json?\s*", "", raw)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        # Find the JSON object
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            # Validate expected keys
            expected = {"metric", "aggregation", "group_by", "operation", "filters", "time_grain"}
            if expected.intersection(parsed.keys()):
                logger.info("LLM parsed query: %s", parsed)
                return parsed
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Failed to parse LLM JSON: %s — raw: %s", e, raw[:200])

    return None


def generate_insight(query: str, intent: str, result: str) -> Optional[str]:
    """
    Use LLM to generate natural-language insights from analysis results.
    Returns insight text or None if LLM is unavailable.
    """
    prompt = _INSIGHT_GENERATION_PROMPT.format(
        intent=intent,
        query=query,
        result=result,
    )
    raw = _call_ollama(prompt, temperature=0.3)
    if not raw:
        return None

    # Clean up response
    insight = raw.strip()
    # Remove any "Here are the insights:" prefix
    insight = re.sub(r"^(here are|the following|based on).*?:\s*", "", insight, flags=re.IGNORECASE)
    return insight if len(insight) > 10 else None


def is_ollama_available() -> bool:
    """Check if Ollama is reachable."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False
