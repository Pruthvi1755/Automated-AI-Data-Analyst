import pandas as pd
from visualization.charts import build_plotly_fig, dark_layout
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_metric_column

def run_anomaly(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.graph_objects as go

    col = detect_metric_column(query, schema.numeric_cols) or schema.numeric_cols[0]
    data = df[col].dropna()
    
    if len(data) < 4:
        return {"result": "Not enough data for anomaly detection.", "insight": "Need at least 4 data points.",
                "figure": None, "metric": col, "aggregation": "iqr_anomaly", "group_by": None, "columns_used": [col]}

    q1, q3 = data.quantile(0.25), data.quantile(0.75)
    iqr = q3 - q1
    lb, ub = q1 - 1.5*iqr, q3 + 1.5*iqr
    mask = (data < lb) | (data > ub)
    anomalies = data[mask]
    normal = data[~mask]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=normal.index.tolist(), y=normal.tolist(), mode="markers",
                             name="Normal", marker=dict(color="#38bdf8", size=5)))
    fig.add_trace(go.Scatter(x=anomalies.index.tolist(), y=anomalies.tolist(), mode="markers",
                             name="Anomaly", marker=dict(color="#ef4444", size=10, symbol="x")))
    fig.add_hline(y=ub, line_dash="dash", line_color="#fbbf24", annotation_text="Upper Bound")
    fig.add_hline(y=lb, line_dash="dash", line_color="#fbbf24", annotation_text="Lower Bound")
    fig.update_layout(title=f"Anomaly Detection: {col}", **dark_layout())
    fig.update_xaxes(gridcolor="#1a2035")
    fig.update_yaxes(gridcolor="#1a2035")

    pct = (len(anomalies) / len(data) * 100)
    insight = (
        f"Found **{len(anomalies)}** anomalies in **{col}** ({pct:.1f}% of data). "
        f"Normal range: [{lb:,.2f}, {ub:,.2f}]. "
        f"Anomalous values range: {anomalies.min():,.2f} – {anomalies.max():,.2f}." if len(anomalies) > 0 else "No anomalies detected."
    )
    return {"result": f"{len(anomalies)} anomalies detected in '{col}' ({pct:.1f}%)", "insight": insight,
            "figure": build_plotly_fig(fig), "metric": col, "aggregation": "iqr_anomaly",
            "group_by": None, "columns_used": [col]}
