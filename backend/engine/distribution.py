import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_metric_column

def run_distribution(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.express as px

    col = detect_metric_column(query, schema.numeric_cols) or schema.numeric_cols[0]
    data = df[col].dropna()
    desc = data.describe()

    fig = apply_dark(px.histogram(
        df, x=col, nbins=40, title=f"Distribution of {col}",
        color_discrete_sequence=["#38bdf8"],
        marginal="box",
    ))

    # Outlier detection via IQR
    q1, q3 = data.quantile(0.25), data.quantile(0.75)
    iqr = q3 - q1
    outliers = data[(data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)]
    skew = data.skew()
    skew_label = "right-skewed" if skew > 0.5 else "left-skewed" if skew < -0.5 else "approximately normal"

    insight = (
        f"**{col}** ranges from **{desc['min']:,.2f}** to **{desc['max']:,.2f}** "
        f"with mean **{desc['mean']:,.2f}** and std **{desc['std']:,.2f}**. "
        f"Distribution is **{skew_label}** (skew={skew:.2f}). "
        f"Detected **{len(outliers)}** outliers via IQR method."
    )
    result_str = f"mean={desc['mean']:.4f} | std={desc['std']:.4f} | min={desc['min']:.4f} | max={desc['max']:.4f} | outliers={len(outliers)}"
    return {"result": result_str, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": col, "aggregation": "distribution", "group_by": None, "columns_used": [col]}
