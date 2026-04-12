import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_multi_columns

def run_correlation(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.express as px

    if len(schema.numeric_cols) < 2:
        return {"result": "Need ≥2 numeric columns for correlation.", "insight": "Insufficient data.",
                "figure": None, "metric": "correlation", "aggregation": "pearson", "group_by": None, "columns_used": []}

    cols = detect_multi_columns(query, schema.numeric_cols, min_score=0.1) or schema.numeric_cols
    corr_df = df[cols].corr()

    fig = apply_dark(px.imshow(
        corr_df, text_auto=".2f",
        color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#0a0e1a"], [1, "#dc2626"]],
        title="Pearson Correlation Heatmap", zmin=-1, zmax=1,
    ))

    # Top pairs
    pairs = []
    for i, c1 in enumerate(cols):
        for c2 in cols[i+1:]:
            pairs.append((c1, c2, corr_df.loc[c1, c2]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)

    top_lines = [f"**{c1}** ↔ **{c2}**: {v:+.3f} ({'strong' if abs(v) > 0.7 else 'moderate' if abs(v) > 0.4 else 'weak'})" for c1, c2, v in pairs[:3]]
    insight = "Top correlations: " + " | ".join(top_lines)

    return {"result": insight, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": "correlation", "aggregation": "pearson", "group_by": None, "columns_used": cols}
