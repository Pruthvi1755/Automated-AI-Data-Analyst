"""
schema.py — Schema detection for uploaded datasets.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class DataSchema:
    numeric_cols: list[str] = field(default_factory=list)
    categorical_cols: list[str] = field(default_factory=list)
    datetime_cols: list[str] = field(default_factory=list)
    all_cols: list[str] = field(default_factory=list)

    def has_numeric(self) -> bool:
        return bool(self.numeric_cols)

    def has_datetime(self) -> bool:
        return bool(self.datetime_cols)

    def has_categorical(self) -> bool:
        return bool(self.categorical_cols)

    def summary(self) -> str:
        return (
            f"Numeric: {self.numeric_cols} | "
            f"Categorical: {self.categorical_cols} | "
            f"Datetime: {self.datetime_cols}"
        )


def detect_schema(df: pd.DataFrame) -> DataSchema:
    """Auto-detect column types from a DataFrame."""
    schema = DataSchema(all_cols=list(df.columns))
    if df is None or df.empty:
        return schema

    for col in df.columns:
        dtype = df[col].dtype

        if pd.api.types.is_datetime64_any_dtype(dtype):
            schema.datetime_cols.append(col)
        elif pd.api.types.is_numeric_dtype(dtype):
            unique_ratio = df[col].nunique() / max(len(df), 1)
            # Low-cardinality integers → treat as categorical
            if (
                pd.api.types.is_integer_dtype(dtype)
                and unique_ratio < 0.05
                and df[col].nunique() <= 20
            ):
                schema.categorical_cols.append(col)
            else:
                schema.numeric_cols.append(col)
        else:
            schema.categorical_cols.append(col)

    return schema
