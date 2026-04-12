import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_multi_columns

def run_trend(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.express as px

    y_cols = detect_multi_columns(query, schema.numeric_cols, min_score=0.3) or schema.numeric_cols[:2]
    y_cols = y_cols[:4]  # Cap at 4 lines

    # Determine default aggregation method based on column name
    # e.g., if it's "revenue", "sales", "amount", we should SUM when resampling
    # but we can do it per-column
    agg_funcs = {}
    for c in y_cols:
        c_lower = c.lower()
        if any(w in c_lower for w in ["revenue", "sales", "total", "amount", "profit", "income", "qty", "quantity", "volume", "spend"]):
            agg_funcs[c] = 'sum'
        else:
            agg_funcs[c] = 'mean'

    if schema.has_datetime():
        x_col = schema.datetime_cols[0]
        plot_df = df[[x_col] + [c for c in y_cols if c in df.columns]].dropna().sort_values(x_col)
        # Resample if dense
        try:
            # Resample dynamically based on agg_funcs mapping
            temp = plot_df.set_index(x_col).resample("ME").agg(agg_funcs).reset_index()
            if len(temp) >= 3: 
                plot_df = temp
        except Exception as e:
            pass
    else:
        plot_df = df.copy()
        plot_df["_index"] = range(len(df))
        x_col = "_index"

    fig = apply_dark(px.line(
        plot_df, x=x_col, y=y_cols,
        title=f"Trend: {', '.join(y_cols)}",
        markers=True, color_discrete_sequence=["#38bdf8", "#f472b6", "#34d399", "#fbbf24"],
    ))

    stats = []
    for c in y_cols:
        if c in df.columns:
            s, e = df[c].iloc[0], df[c].iloc[-1]
            chg = ((e - s) / max(abs(s), 1)) * 100
            stats.append(f"**{c}**: {s:,.2f} → {e:,.2f} ({'↑' if chg > 0 else '↓'} {abs(chg):.1f}%)")

    insight = " | ".join(stats) or "Trend analysis complete."
    return {"result": insight, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": ", ".join(y_cols), "aggregation": "trend", "group_by": x_col, "columns_used": y_cols}
