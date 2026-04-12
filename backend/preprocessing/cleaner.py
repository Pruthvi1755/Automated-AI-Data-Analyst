"""
cleaner.py — Data cleaning, type coercion, and category normalization.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

# ─── Category Corrections ────────────────────────────────────────────────────
# Maps messy values → canonical form.  Case-insensitive matching.
_CATEGORY_CORRECTIONS: dict[str, str] = {
    # Payment methods
    "up i": "UPI",
    "u p i": "UPI",
    "upi": "UPI",
    "cash on delivery": "COD",
    "cod": "COD",
    "credit card": "Credit Card",
    "debit card": "Debit Card",
    "net banking": "Net Banking",
    # Food / product categories
    "snaks": "Snacks",
    "snack": "Snacks",
    "snacks": "Snacks",
    "diary": "Dairy",
    "dairy": "Dairy",
    "beverages": "Beverages",
    "beverage": "Beverages",
    "fruits": "Fruits",
    "fruit": "Fruits",
    "vegetables": "Vegetables",
    "vegetable": "Vegetables",
    "vegtable": "Vegetables",
    "vegitable": "Vegetables",
}


def _clean_value(val: str) -> str:
    """Strip currency symbols, commas, whitespace from a string value."""
    val = str(val).strip()
    val = re.sub(r"[₹$€£¥,\s]", "", val)
    val = re.sub(r"\+$", "", val)
    if val.startswith("(") and val.endswith(")"):
        val = "-" + val[1:-1]
    return val


def _try_numeric(series: pd.Series) -> pd.Series:
    """Attempt to coerce an object series to numeric."""
    cleaned = series.apply(_clean_value)
    converted = pd.to_numeric(cleaned, errors="coerce")
    non_null = series.notna().sum()
    if non_null == 0:
        return series
    if converted.notna().sum() / non_null >= 0.6:
        return converted
    return series


def _try_datetime(series: pd.Series) -> pd.Series:
    """Attempt to coerce an object series to datetime."""
    try:
        converted = pd.to_datetime(series, dayfirst=True, errors="coerce")
        non_null = series.notna().sum()
        if non_null == 0:
            return series
        if converted.notna().sum() / non_null >= 0.7:
            return converted
    except Exception:
        pass
    return series


def _normalize_categories(series: pd.Series) -> pd.Series:
    """Lowercase, strip, then apply correction dictionary."""
    result = series.copy()
    str_mask = result.apply(lambda x: isinstance(x, str))
    if not str_mask.any():
        return result

    # Lowercase + strip
    result[str_mask] = result[str_mask].str.strip().str.lower()

    # Apply corrections
    result[str_mask] = result[str_mask].map(
        lambda v: _CATEGORY_CORRECTIONS.get(v, v.title()) if isinstance(v, str) else v
    )
    return result


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
    1. Normalize column names
    2. Deduplicate column names
    3. Drop all-null rows/cols
    4. Try numeric coercion
    5. Try datetime coercion (dayfirst=True)
    6. Normalize categorical text
    7. Fill missing values (numeric→median, categorical→mode)
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # ── 1. Normalize column names ─────────────────────────────────────────
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )

    # ── 2. Deduplicate column names ───────────────────────────────────────
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        mask = cols == dup
        cols[mask] = [
            f"{dup}_{i}" if i != 0 else dup
            for i, _ in enumerate(mask[mask].index)
        ]
    df.columns = cols.tolist()

    # ── 3. Drop all-null rows/cols ────────────────────────────────────────
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    if df.empty:
        return df

    # ── 4. Try numeric coercion ───────────────────────────────────────────
    for col in df.select_dtypes(include=["object"]).columns:
        result = _try_numeric(df[col])
        if result.dtype != df[col].dtype:
            df[col] = result

    # ── 5. Try datetime coercion ──────────────────────────────────────────
    for col in df.select_dtypes(include=["object"]).columns:
        result = _try_datetime(df[col])
        if hasattr(result, "dt"):
            df[col] = result

    # ── 6. Normalize categorical text ─────────────────────────────────────
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = _normalize_categories(df[col])

    # ── 7. Fill missing values ────────────────────────────────────────────
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            median_val = df[col].median()
            df[col] = df[col].fillna(0 if pd.isna(median_val) else median_val)
        elif not pd.api.types.is_datetime64_any_dtype(df[col]):
            mode_val = df[col].mode()
            df[col] = df[col].fillna(
                mode_val.iloc[0] if len(mode_val) > 0 else "Unknown"
            )

    return df
