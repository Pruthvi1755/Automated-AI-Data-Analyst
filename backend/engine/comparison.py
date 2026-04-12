import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_metric_column, detect_column, detect_multi_columns

def run_comparison(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.express as px

    y_col = detect_metric_column(query, schema.numeric_cols) or schema.numeric_cols[0]

    # FIX: Check if the column name implies we should use sum instead of mean
    y_col_lower = y_col.lower()
    use_sum = any(w in y_col_lower for w in ["revenue", "sales", "total", "amount", "profit", "income", "qty", "quantity", "volume", "budget", "spend"])
    agg_op = "sum" if use_sum else "mean"
    title_prefix = "Total" if use_sum else "Average"

    if schema.categorical_cols:
        x_col = detect_column(query, schema.categorical_cols, top_n=1)[0]
        
        if use_sum:
            grouped = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
        else:
            grouped = df.groupby(x_col)[y_col].mean().reset_index().sort_values(y_col, ascending=False)
            
        total = grouped[y_col].sum()
        grouped["pct"] = (grouped[y_col] / total * 100).round(1)

        fig = apply_dark(px.bar(
            grouped.head(20), x=x_col, y=y_col,
            title=f"{title_prefix} {y_col} by {x_col}",
            color=y_col, color_continuous_scale=[[0, "#1e3a5f"], [1, "#38bdf8"]],
        ))
        top = grouped.iloc[0]
        insight = (
            f"**{top[x_col]}** has the highest {title_prefix.lower()} **{y_col}** at "
            f"**{top[y_col]:,.2f}** ({top['pct']}% of total)."
        )
        return {"result": insight, "insight": insight, "figure": build_plotly_fig(fig),
                "metric": y_col, "aggregation": agg_op, "group_by": x_col, "columns_used": [y_col, x_col]}

    # Multi-column comparison
    cols = (detect_multi_columns(query, schema.numeric_cols) or schema.numeric_cols)[:6]
    if use_sum:
        vals = [df[c].sum() for c in cols if c in df.columns]
    else:
        vals = [df[c].mean() for c in cols if c in df.columns]
        
    means = pd.DataFrame({"Column": cols, "Value": vals})
    fig = apply_dark(px.bar(means, x="Column", y="Value", title=f"Column Comparison ({title_prefix})",
                             color="Column", color_discrete_sequence=["#38bdf8","#f472b6","#34d399","#fbbf24","#a78bfa","#fb923c"]))
    insight = " | ".join(f"**{row.Column}**: {row.Value:,.2f}" for _, row in means.iterrows())
    return {"result": insight, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": y_col, "aggregation": agg_op, "group_by": None, "columns_used": cols}
