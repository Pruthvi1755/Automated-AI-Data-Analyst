"""
column_mapper.py — Dynamic column intelligence with fuzzy matching.
NEVER hardcodes column names.  Works for ANY dataset.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher

from core.config import REVENUE_KEYWORDS

# ─── Semantic Aliases ─────────────────────────────────────────────────────────
_METRIC_ALIASES: dict[str, list[str]] = {
    "revenue": ["revenue", "sales", "total", "amount", "income", "turnover", "earnings"],
    "profit":  ["profit", "margin", "net", "gain", "earnings"],
    "price":   ["price", "cost", "fee", "rate", "charge", "unit_price"],
    "quantity":["qty", "quantity", "units", "count", "volume"],
    "date":    ["date", "time", "timestamp", "created", "order_date", "period", "month", "year", "day"],
    "location":["city", "region", "location", "country", "state", "area", "territory", "zone"],
    "category":["category", "type", "product", "segment", "group", "class", "brand", "item"],
}

_PRIORITY_KEYWORDS: list[str] = [
    "sales", "revenue", "profit", "total", "amount", "price", "cost",
    "income", "loss", "gross", "net", "value", "qty", "quantity",
    "score", "rating", "count", "units", "volume", "budget", "spend",
]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _fuzzy_score(a: str, b: str) -> float:
    """SequenceMatcher ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _score_col(col: str, query_tokens: list[str]) -> float:
    """Score a column name against query tokens."""
    col_tokens = _tokenize(col)
    score = 0.0
    for qt in query_tokens:
        for ct in col_tokens:
            if qt == ct:
                score += 3.0
            elif qt in ct or ct in qt:
                score += 1.5
            elif len(qt) >= 3 and len(ct) >= 3 and _fuzzy_score(qt, ct) > 0.7:
                score += 1.0
            elif len(qt) >= 3 and qt[:3] == ct[:3]:
                score += 0.5
    for kw in _PRIORITY_KEYWORDS:
        if kw in col.lower():
            score += 0.5
    return score


def detect_column(query: str, columns: list[str], top_n: int = 1) -> list[str]:
    """Find the best-matching column(s) for a query."""
    if not columns:
        return []
    qtoks = _tokenize(query)
    scored = sorted(
        [(c, _score_col(c, qtoks)) for c in columns],
        key=lambda x: x[1],
        reverse=True,
    )
    if scored[0][1] == 0:
        priority = sorted(
            columns,
            key=lambda c: any(kw in c.lower() for kw in _PRIORITY_KEYWORDS),
            reverse=True,
        )
        return priority[:top_n]
    return [c for c, _ in scored[:top_n]]


def detect_multi_columns(
    query: str, columns: list[str], min_score: float = 0.5
) -> list[str]:
    """Detect multiple relevant columns above a score threshold."""
    if not columns:
        return []
    qtoks = _tokenize(query)
    matched = [c for c in columns if _score_col(c, qtoks) >= min_score]
    if not matched:
        return sorted(
            columns,
            key=lambda c: any(kw in c.lower() for kw in _PRIORITY_KEYWORDS),
            reverse=True,
        )[:2]
    return matched


def detect_metric_column(query: str, columns: list[str]) -> str | None:
    """
    Fuzzy-match query metric words to actual column names.
    STRICT: NEVER map 'revenue' to 'price' — these are distinct concepts.
    """
    q_lower = query.lower()

    # Determine which semantic group the query is asking about
    target_group = None
    for metric, aliases in _METRIC_ALIASES.items():
        for alias in aliases:
            if alias in q_lower:
                target_group = metric
                break
        if target_group:
            break

    if target_group:
        # STRICT: revenue ≠ price
        aliases = _METRIC_ALIASES[target_group]
        for col in columns:
            col_lower = col.lower()
            for alias in aliases:
                if alias in col_lower or col_lower in alias:
                    return col

        # Fuzzy fallback within the same group
        best_col, best_score = None, 0.0
        for col in columns:
            for alias in aliases:
                s = _fuzzy_score(col.lower(), alias)
                if s > best_score and s > 0.6:
                    best_col, best_score = col, s
        if best_col:
            return best_col

    # General fallback — best scored column
    return detect_column(query, columns, top_n=1)[0] if columns else None


def is_revenue_column(col: str) -> bool:
    """Check if a column name semantically represents revenue/sales/amount."""
    col_lower = col.lower()
    return any(kw in col_lower for kw in REVENUE_KEYWORDS)
