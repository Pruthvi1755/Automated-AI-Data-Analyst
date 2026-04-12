import pandas as pd
from visualization.charts import build_plotly_fig, apply_dark
from preprocessing.schema import DataSchema
from intelligence.column_mapper import detect_metric_column

def run_feature_importance(query: str, df: pd.DataFrame, schema: DataSchema) -> dict:
    import plotly.express as px
    try:
        from sklearn.ensemble import RandomForestRegressor
    except ImportError:
        return {"result": "sklearn not installed.", "insight": "Feature importance requires scikit-learn.",
                "figure": None, "metric": "", "aggregation": "feature_importance", "group_by": None, "columns_used": []}

    target_col = detect_metric_column(query, schema.numeric_cols) or schema.numeric_cols[0]
    
    # Use other numeric columns as features
    feature_cols = [c for c in schema.numeric_cols if c != target_col]
    
    if len(feature_cols) == 0:
        return {"result": "Not enough numeric columns.", "insight": "Need at least one feature column to determine importance.",
                "figure": None, "metric": target_col, "aggregation": "feature_importance", "group_by": None, "columns_used": [target_col]}

    # Drop missing values for training
    train_df = df[feature_cols + [target_col]].dropna()
    
    if len(train_df) < 10:
        return {"result": "Insufficient data.", "insight": "Need more complete rows to train the model.",
                "figure": None, "metric": target_col, "aggregation": "feature_importance", "group_by": None, "columns_used": [target_col] + feature_cols}

    X = train_df[feature_cols]
    y = train_df[target_col]
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    importances = model.feature_importances_
    imp_df = pd.DataFrame({"Feature": feature_cols, "Importance": importances})
    imp_df = imp_df.sort_values(by="Importance", ascending=False).head(10)
    
    fig = apply_dark(px.bar(
        imp_df, x="Importance", y="Feature", orientation='h', title=f"What drives {target_col}?",
        color="Importance", color_continuous_scale=[[0, "#1e3a5f"], [1, "#f472b6"]]
    ))
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    top_feature = imp_df.iloc[0]
    insight = (
        f"**{top_feature['Feature']}** is the strongest driver for **{target_col}**, "
        f"with an importance score of **{top_feature['Importance']:.2%}**. "
        f"Top 3 factors explain **{imp_df.head(3)['Importance'].sum():.2%}** of the variance."
    )
    result_str = f"Top driver: {top_feature['Feature']} ({top_feature['Importance']:.2%})"
    return {"result": result_str, "insight": insight, "figure": build_plotly_fig(fig),
            "metric": target_col, "aggregation": "feature_importance", "group_by": None, "columns_used": [target_col] + feature_cols}
