import json

def build_plotly_fig(fig_dict) -> dict:
    """Convert plotly figure to JSON-serializable dict."""
    try:
        import plotly.io as pio
        return json.loads(pio.to_json(fig_dict))
    except Exception:
        return {}

def dark_layout() -> dict:
    return dict(
        font=dict(family="'DM Mono', monospace", size=12),
        plot_bgcolor="#0a0e1a",
        paper_bgcolor="#0a0e1a",
        font_color="#94a3b8",
        title_font_size=14,
        title_font_color="#e2e8f0",
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e293b"),
        margin=dict(t=50, b=40, l=50, r=20),
    )

def apply_dark(fig):
    fig.update_layout(**dark_layout())
    fig.update_xaxes(gridcolor="#1a2035", zerolinecolor="#2a3550", showline=True, linecolor="#1e293b")
    fig.update_yaxes(gridcolor="#1a2035", zerolinecolor="#2a3550", showline=True, linecolor="#1e293b")
    return fig
