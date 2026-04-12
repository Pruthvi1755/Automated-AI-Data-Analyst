import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_multi_columns

def run_general(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.express as px

    cols = (detect_multi_columns(query, schema.numeric_cols, min_score=0.1) or schema.numeric_cols)[:5]
    means = {c: df[c].mean() for c in cols if c in df.columns}
    means_df = pd.DataFrame(list(means.items()), columns=["Column", "Mean"])

    if means_df.empty:
        return {"result": "No numeric data found.", "insight": "Cannot compute summary without numeric columns.",
                "figure": None, "metric": "summary", "aggregation": "descriptive", "group_by": None, "columns_used": []}

    fig = apply_dark(px.bar(means_df, x="Column", y="Mean", title="Summary Statistics",
                             color="Column", color_discrete_sequence=["#38bdf8","#f472b6","#34d399","#fbbf24","#a78bfa"]))
    stats = " | ".join(f"**{c}**: mean={v:,.2f}" for c, v in means.items())
    insight = f"Dataset summary — {stats}. Total of {len(df):,} rows, {len(schema.all_cols)} columns."
    return {"result": stats, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": "summary", "aggregation": "descriptive", "group_by": None, "columns_used": cols}
