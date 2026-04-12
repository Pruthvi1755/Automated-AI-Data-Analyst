import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from core.state import app_state
from core.config import REPORTS_DIR
from routes.upload import generate_suggestions

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0 (Autonomous)"}

@router.get("/history")
def get_history():
    return {"history": list(app_state.history)}

@router.get("/suggestions")
def get_suggestions_route():
    schema = app_state.schema
    if not schema:
        return {"suggestions": [
            "Upload a dataset to get query suggestions",
            "What is the average sales?",
            "Show the trend over time",
        ]}
    return {"suggestions": generate_suggestions(schema)}

@router.get("/report/{filename}")
def get_report(filename: str):
    path = REPORTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Report not found.")
    return FileResponse(str(path), media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.get("/summary")
def get_summary():
    df = app_state.df
    schema = app_state.schema
    if df is None:
        return {"loaded": False}

    stats = {}
    for col in (schema.numeric_cols if schema else [])[:10]:
        try:
            stats[col] = {
                "mean": round(float(df[col].mean()), 4),
                "min":  round(float(df[col].min()), 4),
                "max":  round(float(df[col].max()), 4),
                "std":  round(float(df[col].std()), 4),
                "null_pct": round(float(df[col].isna().mean() * 100), 2),
            }
        except Exception:
            pass

    return {
        "loaded": True,
        "filename": app_state.filename,
        "rows": len(df),
        "cols": len(df.columns),
        "schema": {
            "numeric": schema.numeric_cols if schema else [],
            "categorical": schema.categorical_cols if schema else [],
            "datetime": schema.datetime_cols if schema else [],
        },
        "stats": stats,
        "suggestions": generate_suggestions(schema) if schema else [],
    }
