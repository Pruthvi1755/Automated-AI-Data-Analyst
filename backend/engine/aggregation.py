"""
aggregation.py — Aggregation engine with SUM-first defaults for revenue columns.
"""
import logging
import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_metric_column, detect_column, is_revenue_column

logger = logging.getLogger("ai_analyst.engine.aggregation")


def run_aggregation(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    col = detect_metric_column(query, schema.numeric_cols) or schema.numeric_cols[0]
    q = query.lower()

    # Determine aggregation operation
    # FIX: Default to SUM for revenue/sales/amount columns instead of MEAN
    if any(w in q for w in ["sum", "total"]):
        op, val = "sum", df[col].sum()
    elif any(w in q for w in ["max", "maximum", "highest", "largest", "top"]):
        op, val = "max", df[col].max()
    elif any(w in q for w in ["min", "minimum", "lowest", "smallest"]):
        op, val = "min", df[col].min()
    elif "median" in q:
        op, val = "median", df[col].median()
    elif any(w in q for w in ["std", "standard deviation", "variance"]):
        op, val = "std", df[col].std()
    elif any(w in q for w in ["count", "how many"]):
        op, val = "count", df[col].count()
    elif any(w in q for w in ["average", "mean", "avg"]):
        op, val = "mean", df[col].mean()
    elif is_revenue_column(col):
        # Revenue-type columns default to SUM
        op, val = "sum", df[col].sum()
    else:
        op, val = "mean", df[col].mean()

    raw = f"{op.capitalize()} of '{col}' = {val:,.4f}"
    fig = None

    # Group by categorical if relevant
    if schema.categorical_cols:
        group_col = detect_column(query, schema.categorical_cols, top_n=1)[0]
        try:
            import plotly.express as px
            grouped = df.groupby(group_col)[col].agg(op).reset_index().sort_values(col, ascending=False)
            grouped.columns = [group_col, col]
            total = grouped[col].sum()
            grouped["pct"] = (grouped[col] / total * 100).round(1) if total != 0 else 0

            fig = apply_dark(px.bar(
                grouped.head(20), x=group_col, y=col,
                title=f"{op.capitalize()} of {col} by {group_col}",
                color=col, color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#2563eb"], [1, "#38bdf8"]],
                text=grouped.head(20)["pct"].astype(str) + "%"
            ))
            fig.update_traces(textposition="outside")

            top_row = grouped.iloc[0]
            insight = (
                f"**{top_row[group_col]}** leads with {op} {col} of "
                f"**{top_row[col]:,.2f}** ({top_row['pct']}% of total). "
                f"The dataset spans {len(grouped)} {group_col} groups."
            )
            return {
                "result": raw, "insight": insight, "figure": build_plotly_fig(fig),
                "metric": col, "aggregation": op, "group_by": group_col,
                "columns_used": [col, group_col],
            }
        except Exception as e:
            logger.warning("Grouped aggregation failed: %s", e)

    insight = f"The {op} of **{col}** across {len(df):,} records is **{val:,.4f}**."
    return {
        "result": raw, "insight": insight, "figure": None,
        "metric": col, "aggregation": op, "group_by": None,
        "columns_used": [col],
    }