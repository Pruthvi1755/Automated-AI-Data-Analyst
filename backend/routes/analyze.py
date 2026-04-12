"""
analyze.py — /analyze endpoint orchestrating the full pipeline.
"""
import uuid
import logging
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.state import app_state
from intelligence.query_classifier import classify_query
from engine import (
    run_aggregation, run_trend, run_correlation, run_comparison,
    run_prediction, run_distribution, run_anomaly, run_general,
    run_feature_importance
)
from reports.pdf_generator import generate_pdf_report
from intelligence.llm_client import generate_insight

logger = logging.getLogger("ai_analyst.analyze")
router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/analyze")
async def analyze(req: QueryRequest):
    """Run analysis on uploaded dataset."""
    df = app_state.df
    schema = app_state.schema

    if df is None:
        raise HTTPException(400, "No dataset loaded. Upload a file first.")

    query = req.query.strip()
    if len(query) < 3:
        raise HTTPException(400, "Query too short.")
    if len(query) > 2000:
        raise HTTPException(400, "Query too long (max 2000 chars).")
    if not any(c.isalpha() for c in query):
        raise HTTPException(400, "Query must contain letters.")

    # 1. Classification (Hybrid LLM + Keyword)
    intent, llm_parsed = classify_query(query, schema.all_cols)
    confidence = 0.9 if llm_parsed else 0.6

    handlers = {
        "aggregation":        run_aggregation,
        "trend":              run_trend,
        "correlation":        run_correlation,
        "comparison":         run_comparison,
        "prediction":         run_prediction,
        "distribution":       run_distribution,
        "anomaly":            run_anomaly,
        "feature_importance": run_feature_importance,
        "general":            run_general,
    }

    try:
        engine_logic = handlers.get(intent, run_general)
        analysis = engine_logic(query, df, schema)
    except Exception as e:
        logger.exception("Analysis failed: %s", e)
        raise HTTPException(500, f"Analysis failed: {e}")

    # LLM Insight Generation (Enhancement)
    try:
        enhanced_insight = generate_insight(
            query=query,
            intent=intent,
            result=analysis.get("result", ""),
        )
        if enhanced_insight:
            analysis["insight"] = enhanced_insight
    except Exception as e:
        logger.warning("LLM insight generation failed: %s", e)

    # Build PDF
    pdf_path = None
    try:
        pdf_path = generate_pdf_report(
            query=query,
            intent=intent,
            result=analysis["result"],
            insight=analysis["insight"],
            fig_dict=analysis.get("figure"),
        )
    except Exception as e:
        logger.warning("PDF generation failed: %s", e)

    pdf_link = f"/report/{pdf_path.name}" if pdf_path else None

    response = {
        "query": query,
        "intent": intent,
        "confidence_score": confidence,
        "metric": analysis.get("metric", ""),
        "aggregation": analysis.get("aggregation", ""),
        "group_by": analysis.get("group_by"),
        "result": analysis["result"],
        "insight": analysis["insight"],
        "graph": analysis.get("figure"),
        "pdf_link": pdf_link,
        "columns_used": analysis.get("columns_used", []),
    }

    # FIFO history
    history_entry = {
        "id": str(uuid.uuid4())[:8],
        "query": query,
        "intent": intent,
        "insight": analysis["insight"],
        "timestamp": pd.Timestamp.now().isoformat(),
    }
    app_state.history.appendleft(history_entry)

    return response
