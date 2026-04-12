import io
import pandas as pd
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException
from core.state import app_state
from preprocessing.cleaner import clean_dataframe
from preprocessing.schema import detect_schema

router = APIRouter()

def generate_suggestions(schema) -> list[str]:
    suggestions = []
    if schema.numeric_cols:
        c = schema.numeric_cols[0]
        suggestions.append(f"What is the average {c}?")
        suggestions.append(f"Show distribution of {c}")
        if len(schema.numeric_cols) >= 2:
            suggestions.append(f"What is the correlation between {schema.numeric_cols[0]} and {schema.numeric_cols[1]}?")
    if schema.categorical_cols and schema.numeric_cols:
        suggestions.append(f"Compare {schema.numeric_cols[0]} by {schema.categorical_cols[0]}")
        suggestions.append(f"Top {schema.categorical_cols[0]} by {schema.numeric_cols[0]}")
    if schema.datetime_cols and schema.numeric_cols:
        suggestions.append(f"Show trend of {schema.numeric_cols[0]} over time")
        suggestions.append(f"Predict future {schema.numeric_cols[0]}")
    suggestions.append(f"Detect anomalies in {schema.numeric_cols[0] if schema.numeric_cols else 'data'}")
    return suggestions[:8]

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept CSV or XLSX, clean it, detect schema, return summary."""
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "Only CSV and XLSX files are supported.")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 50MB).")

    try:
        if file.filename.lower().endswith(".csv"):
            df_raw = pd.read_csv(io.BytesIO(content))
        else:
            df_raw = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    except Exception as e:
        raise HTTPException(400, f"Failed to parse file: {e}")

    df_clean = clean_dataframe(df_raw)
    schema = detect_schema(df_clean)

    app_state.df = df_clean
    app_state.schema = schema
    app_state.filename = file.filename
    app_state.history.clear()

    # Quick stats
    stats = {}
    for col in schema.numeric_cols[:10]:
        try:
            stats[col] = {
                "mean": round(float(df_clean[col].mean()), 4),
                "min":  round(float(df_clean[col].min()), 4),
                "max":  round(float(df_clean[col].max()), 4),
                "std":  round(float(df_clean[col].std()), 4),
            }
        except Exception:
            pass

    preview = df_clean.head(20).replace({np.nan: None})
    # Convert to JSON-safe format
    preview_records = []
    for rec in preview.to_dict("records"):
        safe_rec = {}
        for k, v in rec.items():
            if isinstance(v, (pd.Timestamp,)):
                safe_rec[k] = str(v)
            elif isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                safe_rec[k] = None
            else:
                safe_rec[k] = v
        preview_records.append(safe_rec)

    return {
        "filename": file.filename,
        "rows": len(df_clean),
        "cols": len(df_clean.columns),
        "schema": {
            "numeric": schema.numeric_cols,
            "categorical": schema.categorical_cols,
            "datetime": schema.datetime_cols,
            "all": schema.all_cols,
        },
        "stats": stats,
        "preview": preview_records,
        "suggestions": generate_suggestions(schema),
    }

