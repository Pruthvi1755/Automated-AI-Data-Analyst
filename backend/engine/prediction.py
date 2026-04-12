import numpy as np
import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark, dark_layout
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_metric_column

def run_prediction(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.graph_objects as go
    from sklearn.linear_model import LinearRegression

    col = detect_metric_column(query, schema.numeric_cols) or schema.numeric_cols[0]
    y = df[col].dropna().values

    if len(y) < 5:
        return {"result": f"Need ≥5 data points, got {len(y)}.", "insight": "Insufficient data.",
                "figure": None, "metric": col, "aggregation": "linear_regression", "group_by": None, "columns_used": [col]}

    X = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression().fit(X, y)
    score = model.score(X, y)
    steps = 10
    future_X = np.arange(len(y), len(y) + steps).reshape(-1, 1)
    preds = model.predict(future_X)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(y))), y=y.tolist(), name="Actual",
                             line=dict(color="#38bdf8", width=2), mode="lines+markers"))
    fig.add_trace(go.Scatter(x=list(range(len(y), len(y)+steps)), y=preds.tolist(), name="Predicted",
                             line=dict(color="#f472b6", width=2, dash="dot"), mode="lines+markers"))
    fig.update_layout(title=f"Prediction: {col} (R²={score:.3f})", **dark_layout())
    fig.update_xaxes(gridcolor="#1a2035", zerolinecolor="#2a3550")
    fig.update_yaxes(gridcolor="#1a2035", zerolinecolor="#2a3550")

    trend = "upward ↑" if preds[-1] > y[-1] else "downward ↓"
    pct = ((preds[-1] - y[-1]) / max(abs(y[-1]), 1)) * 100
    insight = (
        f"Predicted **{col}** shows a **{trend}** trend over the next {steps} periods. "
        f"From current **{y[-1]:,.2f}** → projected **{preds[-1]:,.2f}** ({pct:+.1f}%). "
        f"Model R²={score:.3f}."
    )
    result_str = f"Next {steps} predictions for '{col}': {[round(p,2) for p in preds]}. R²={score:.3f}"
    return {"result": result_str, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": col, "aggregation": "linear_regression", "group_by": None, "columns_used": [col]}
