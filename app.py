"""
Pharmacy POS Dashboard — main application.
Run with: python app.py
Then open http://localhost:8050 in your browser.
"""
import platform
from datetime import date

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import pandas as pd

import config
import data as data_module

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    title="Point of Sale Summary",
    update_title=None,
)
server = app.server  # for gunicorn if needed

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def fmt_date(d):
    """Format a date cross-platform (no leading zero on day)."""
    if not hasattr(d, "strftime"):
        return str(d)
    fmt = "%#d/%m/%Y" if platform.system() == "Windows" else "%-d/%m/%Y"
    return d.strftime(fmt)


def fmt_value(val, fmt: str) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if fmt == "currency":
        return f"${val:,.2f}"
    if fmt == "number":
        return f"{val:,.0f}"
    if fmt == "number_2dp":
        return f"{val:,.2f}"
    if fmt == "percentage":
        return f"{val:.2f}%"
    return str(val)


def fmt_diff(val, fmt: str):
    """Return (formatted string with arrow, is_positive)."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—", True
    positive = val >= 0
    arrow = "▲" if positive else "▼"
    if fmt == "currency":
        return f"{arrow} ${abs(val):,.0f}", positive
    if fmt in ("number", "number_2dp"):
        return f"{arrow} {abs(val):,.0f}", positive
    return f"{arrow} {val:,.2f}", positive


def fmt_pct(val) -> tuple[str, bool]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—", True
    positive = val >= 0
    arrow = "▲" if positive else "▼"
    return f"{arrow} {abs(val):.1f}%", positive


# ---------------------------------------------------------------------------
# Metric aggregation
# ---------------------------------------------------------------------------
MONTH_LABELS = config.FY_MONTH_LABELS  # Jul..Jun


def aggregate_monthly(df: pd.DataFrame, agg: str) -> pd.Series:
    """Return a Series indexed 1-12 (FY months) with aggregated values."""
    if df.empty:
        return pd.Series(dtype=float)
    grouped = df.groupby("fy_month")["value"]
    if agg == "average":
        return grouped.mean()
    return grouped.sum()


def get_ytd(df: pd.DataFrame, agg: str, current_fy: str):
    sub = df[df["fy_year"] == current_fy]
    if sub.empty:
        return None
    if agg == "average":
        return sub["value"].mean()
    return sub["value"].sum()


def get_ytd_to_month(df: pd.DataFrame, agg: str, fy: str, max_month: int):
    """YTD for a prior year capped at the same FY month as current year."""
    sub = df[(df["fy_year"] == fy) & (df["fy_month"] <= max_month)]
    if sub.empty:
        return None
    if agg == "average":
        return sub["value"].mean()
    return sub["value"].sum()


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------
def card(children, style=None):
    base = {
        "backgroundColor": config.COLORS["card"],
        "border": f"1px solid {config.COLORS['card_border']}",
        "borderRadius": "8px",
        "padding": "20px",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base)


def setup_message():
    return html.Div([
        html.H2("Setup Required", style={"color": config.COLORS["text"], "marginBottom": "16px"}),
        html.P(
            "Google Sheets credentials not found. Please follow the setup guide to connect your data.",
            style={"color": config.COLORS["text_muted"], "marginBottom": "12px"},
        ),
        html.P(
            f"Expected credentials at: {config.CREDENTIALS_FILE}",
            style={"color": config.COLORS["text_muted"], "fontFamily": "monospace", "fontSize": "13px"},
        ),
        html.P(
            "See setup_guide.md in this folder for step-by-step instructions.",
            style={"color": config.COLORS["text_muted"]},
        ),
    ], style={
        "textAlign": "center",
        "padding": "60px",
        "backgroundColor": config.COLORS["card"],
        "borderRadius": "12px",
        "margin": "40px auto",
        "maxWidth": "600px",
        "border": f"1px solid {config.COLORS['card_border']}",
    })


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
DROPDOWN_OPTIONS = [{"label": name, "value": name} for name in config.METRICS]

app.layout = html.Div(
    style={
        "backgroundColor": config.COLORS["background"],
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "color": config.COLORS["text"],
        "padding": "24px",
    },
    children=[
        # Auto-refresh interval (every 5 minutes)
        dcc.Interval(id="interval-refresh", interval=config.CACHE_TTL * 1000, n_intervals=0),

        # Store for data-ready flag
        dcc.Store(id="data-store"),

        # ── Header ──────────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.H1(
                    "Point of Sale Summary",
                    style={"margin": "0", "fontSize": "28px", "fontWeight": "700",
                           "color": config.COLORS["text"]},
                ),
            ]),
            html.Div([
                html.Span("Most Recent Data From: ", style={"color": config.COLORS["text_muted"],
                                                             "fontSize": "14px"}),
                html.Span(id="last-data-date", style={"color": config.COLORS["accent_light"],
                                                       "fontWeight": "600", "fontSize": "14px"}),
            ]),
        ], style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "marginBottom": "24px",
            "paddingBottom": "16px",
            "borderBottom": f"1px solid {config.COLORS['card_border']}",
        }),

        # ── View By dropdown ─────────────────────────────────────────────────
        html.Div([
            html.Label("View By", style={"color": config.COLORS["text_muted"],
                                          "fontSize": "13px", "marginBottom": "6px",
                                          "display": "block"}),
            dcc.Dropdown(
                id="metric-dropdown",
                options=DROPDOWN_OPTIONS,
                value="Daily Sales",
                clearable=False,
                style={"width": "320px"},
                className="metric-dropdown",
            ),
            html.Style("""
                .metric-dropdown .Select-value-label { color: #ffffff !important; }
                .metric-dropdown .Select-control { background-color: #16213e !important; border-color: #0f3460 !important; }
                .metric-dropdown .Select-menu-outer { background-color: #16213e !important; border-color: #0f3460 !important; }
                .metric-dropdown .Select-option { background-color: #16213e !important; color: #ffffff !important; }
                .metric-dropdown .Select-option:hover { background-color: #0f3460 !important; }
                .metric-dropdown .Select-placeholder { color: #a0a0b8 !important; }
                .metric-dropdown input { color: #ffffff !important; }
                .metric-dropdown .Select-arrow { border-top-color: #a0a0b8 !important; }
            """),
        ], style={"marginBottom": "24px"}),

        # ── Main content (hidden until data loads) ───────────────────────────
        html.Div(id="main-content"),
    ],
)


# ---------------------------------------------------------------------------
# Main content builder (called in callback)
# ---------------------------------------------------------------------------
def build_main_content(metric_name: str, all_data: dict):
    meta = config.METRICS[metric_name]
    key = meta["key"]
    fmt = meta["format"]
    agg = meta["aggregation"]

    current_fy = data_module.get_current_fy()
    prior_fy = data_module.get_prior_fy(current_fy, 1)
    two_yr_fy = data_module.get_prior_fy(current_fy, 2)

    metric_df = data_module.get_metric_data(all_data, key)

    # ── Current max FY month (for fair YTD comparison) ────────────────────
    today = date.today()
    current_fy_month = data_module.get_fy_month(today)

    # ── YTD values ────────────────────────────────────────────────────────
    ytd_cy = get_ytd(metric_df, agg, current_fy)
    ytd_py = get_ytd_to_month(metric_df, agg, prior_fy, current_fy_month) if prior_fy else None
    ytd_2yr = get_ytd_to_month(metric_df, agg, two_yr_fy, current_fy_month) if two_yr_fy else None

    diff_py = (ytd_cy - ytd_py) if (ytd_cy is not None and ytd_py is not None) else None
    diff_2yr = (ytd_cy - ytd_2yr) if (ytd_cy is not None and ytd_2yr is not None) else None
    pct_py = (diff_py / ytd_py * 100) if (diff_py is not None and ytd_py and ytd_py != 0) else None
    pct_2yr = (diff_2yr / ytd_2yr * 100) if (diff_2yr is not None and ytd_2yr and ytd_2yr != 0) else None

    diff_py_str, diff_py_pos = fmt_diff(diff_py, fmt)
    diff_2yr_str, diff_2yr_pos = fmt_diff(diff_2yr, fmt)
    pct_py_str, pct_py_pos = fmt_pct(pct_py)
    pct_2yr_str, pct_2yr_pos = fmt_pct(pct_2yr)

    # ── Last 10 days ──────────────────────────────────────────────────────
    cy_df = metric_df[metric_df["fy_year"] == current_fy].sort_values("date", ascending=False)
    last10 = cy_df.head(10)[["date", "value"]].copy()
    last10["date_str"] = last10["date"].apply(fmt_date)
    last10["value_str"] = last10["value"].apply(lambda v: fmt_value(v, fmt))

    # ── Monthly aggregates ────────────────────────────────────────────────
    cy_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == current_fy], agg)
    py_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == prior_fy], agg) if prior_fy else pd.Series(dtype=float)
    twoyr_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == two_yr_fy], agg) if two_yr_fy else pd.Series(dtype=float)

    months = list(range(1, 13))

    def safe_get(series, m):
        return series.get(m, None)

    # ── Line chart ────────────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MONTH_LABELS,
        y=[safe_get(cy_monthly, m) for m in months],
        mode="lines+markers",
        name=current_fy,
        line=dict(color=config.COLORS["line_cy"], width=2.5),
        marker=dict(size=6),
        connectgaps=False,
    ))
    if prior_fy:
        fig.add_trace(go.Scatter(
            x=MONTH_LABELS,
            y=[safe_get(py_monthly, m) for m in months],
            mode="lines+markers",
            name=prior_fy,
            line=dict(color=config.COLORS["line_py"], width=2),
            marker=dict(size=5),
            connectgaps=False,
        ))
    if two_yr_fy:
        fig.add_trace(go.Scatter(
            x=MONTH_LABELS,
            y=[safe_get(twoyr_monthly, m) for m in months],
            mode="lines+markers",
            name=two_yr_fy,
            line=dict(color=config.COLORS["line_2yr"], width=2),
            marker=dict(size=5),
            connectgaps=False,
        ))

    fig.update_layout(
        plot_bgcolor=config.COLORS["card"],
        paper_bgcolor=config.COLORS["card"],
        font=dict(color=config.COLORS["text"], size=12),
        title=dict(text=metric_name, font=dict(size=16, color=config.COLORS["text"])),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(color=config.COLORS["text"]),
        ),
        xaxis=dict(
            gridcolor="#2a2a4a",
            showline=True,
            linecolor=config.COLORS["card_border"],
        ),
        yaxis=dict(
            gridcolor="#2a2a4a",
            showline=True,
            linecolor=config.COLORS["card_border"],
            tickformat=",.0f",
        ),
        margin=dict(l=60, r=20, t=50, b=40),
        hovermode="x unified",
    )

    # ── Comparison table rows ─────────────────────────────────────────────
    def row_vals(series):
        return [fmt_value(safe_get(series, m), fmt) for m in months]

    def diff_vals(s1, s2):
        out = []
        for m in months:
            v1, v2 = safe_get(s1, m), safe_get(s2, m)
            if v1 is not None and v2 is not None:
                out.append(v1 - v2)
            else:
                out.append(None)
        return out

    def pct_vals(diffs, base):
        out = []
        for m in months:
            d = diffs[m - 1]
            b = safe_get(base, m)
            if d is not None and b and b != 0:
                out.append(d / b * 100)
            else:
                out.append(None)
        return out

    diffs_py = diff_vals(cy_monthly, py_monthly)
    diffs_2yr = diff_vals(cy_monthly, twoyr_monthly)
    pcts_py = pct_vals(diffs_py, py_monthly)
    pcts_2yr = pct_vals(diffs_2yr, twoyr_monthly)

    def color_cells(vals, is_pct=False):
        colors = []
        for v in vals:
            if v is None:
                colors.append(config.COLORS["text_muted"])
            elif v >= 0:
                colors.append(config.COLORS["positive"])
            else:
                colors.append(config.COLORS["negative"])
        return colors

    def arrow_fmt(vals, is_pct=False):
        out = []
        for v in vals:
            if v is None:
                out.append("—")
            elif is_pct:
                arrow = "▲" if v >= 0 else "▼"
                out.append(f"{arrow}{abs(v):.1f}%")
            else:
                arrow = "▲" if v >= 0 else "▼"
                out.append(f"{arrow} {fmt_value(abs(v), fmt)}")
        return out

    table_rows = {
        "CY": row_vals(cy_monthly),
        "PY": row_vals(py_monthly),
        "-2 Yr": row_vals(twoyr_monthly),
        "vs PY": arrow_fmt(diffs_py),
        "vs -2yr": arrow_fmt(diffs_2yr),
        "vs PY%": arrow_fmt(pcts_py, is_pct=True),
        "vs -2yr%": arrow_fmt(pcts_2yr, is_pct=True),
    }
    color_map = {
        "vs PY": color_cells(diffs_py),
        "vs -2yr": color_cells(diffs_2yr),
        "vs PY%": color_cells(pcts_py),
        "vs -2yr%": color_cells(pcts_2yr),
    }

    def make_table_row(label, values, cell_colors=None):
        cells = []
        for i, v in enumerate(values):
            color = cell_colors[i] if cell_colors else config.COLORS["text"]
            cells.append(html.Td(v, style={
                "padding": "7px 12px",
                "textAlign": "right",
                "color": color,
                "fontSize": "13px",
                "borderBottom": f"1px solid {config.COLORS['card_border']}",
            }))
        return html.Tr([
            html.Td(label, style={
                "padding": "7px 12px",
                "fontWeight": "600",
                "color": config.COLORS["text_muted"],
                "fontSize": "13px",
                "whiteSpace": "nowrap",
                "borderBottom": f"1px solid {config.COLORS['card_border']}",
            })
        ] + cells)

    table_header = html.Tr([
        html.Th("", style={"padding": "8px 12px", "backgroundColor": config.COLORS["table_header"]}),
    ] + [
        html.Th(lbl, style={
            "padding": "8px 12px",
            "textAlign": "right",
            "backgroundColor": config.COLORS["table_header"],
            "color": config.COLORS["text"],
            "fontSize": "13px",
            "fontWeight": "600",
        }) for lbl in MONTH_LABELS
    ])

    table_rows_html = [table_header]
    for row_label, vals in table_rows.items():
        table_rows_html.append(
            make_table_row(row_label, vals, color_map.get(row_label))
        )

    # ── Assemble layout ───────────────────────────────────────────────────
    return html.Div([
        # YTD card
        html.Div([
            card([
                html.Div(metric_name, style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"],
                    "marginBottom": "8px", "fontStyle": "italic",
                }),
                html.Div(fmt_value(ytd_cy, fmt), style={
                    "fontSize": "32px", "fontWeight": "700",
                    "color": config.COLORS["text"], "marginBottom": "16px",
                }),
                html.Div("YTD", style={
                    "fontSize": "11px", "color": config.COLORS["text_muted"],
                    "marginBottom": "12px", "textTransform": "uppercase",
                    "letterSpacing": "1px",
                }),
                html.Hr(style={"borderColor": config.COLORS["card_border"], "margin": "12px 0"}),
                html.Div([
                    html.Span(f"vs {prior_fy} YTD  ", style={
                        "fontSize": "13px", "color": config.COLORS["text_muted"],
                    }),
                    html.Span(diff_py_str, style={
                        "fontSize": "14px", "fontWeight": "600",
                        "color": config.COLORS["positive"] if diff_py_pos else config.COLORS["negative"],
                        "marginRight": "10px",
                    }),
                    html.Span(pct_py_str, style={
                        "fontSize": "14px", "fontWeight": "600",
                        "color": config.COLORS["positive"] if pct_py_pos else config.COLORS["negative"],
                    }),
                ], style={"marginBottom": "8px"}),
                html.Div([
                    html.Span(f"vs {two_yr_fy} YTD  " if two_yr_fy else "vs -2yr  ", style={
                        "fontSize": "13px", "color": config.COLORS["text_muted"],
                    }),
                    html.Span(diff_2yr_str, style={
                        "fontSize": "14px", "fontWeight": "600",
                        "color": config.COLORS["positive"] if diff_2yr_pos else config.COLORS["negative"],
                        "marginRight": "10px",
                    }),
                    html.Span(pct_2yr_str, style={
                        "fontSize": "14px", "fontWeight": "600",
                        "color": config.COLORS["positive"] if pct_2yr_pos else config.COLORS["negative"],
                    }),
                ]),
            ], style={"flex": "0 0 300px"}),

        ], style={"display": "flex", "marginBottom": "24px"}),

        # Line chart
        card([
            dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "380px"}),
        ], style={"marginBottom": "24px"}),

        # Monthly comparison table
        card([
            html.Div("Monthly Breakdown", style={
                "fontSize": "13px", "color": config.COLORS["text_muted"],
                "marginBottom": "12px", "fontWeight": "600",
                "textTransform": "uppercase", "letterSpacing": "1px",
            }),
            html.Div([
                html.Table(
                    table_rows_html,
                    style={"width": "100%", "borderCollapse": "collapse"},
                ),
            ], style={"overflowX": "auto"}),
        ], style={"marginBottom": "24px"}),

        # Last 10 days table
        card([
            html.Div("Last 10 Days", style={
                "fontSize": "13px", "color": config.COLORS["text_muted"],
                "marginBottom": "12px", "fontWeight": "600",
                "textTransform": "uppercase", "letterSpacing": "1px",
            }),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Date", style={"padding": "4px 12px", "textAlign": "left",
                                           "color": config.COLORS["text_muted"], "fontSize": "12px"}),
                    html.Th(metric_name, style={"padding": "4px 12px", "textAlign": "right",
                                                 "color": config.COLORS["text_muted"], "fontSize": "12px"}),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(row["date_str"], style={
                            "padding": "5px 12px", "fontSize": "13px",
                            "color": config.COLORS["text"],
                        }),
                        html.Td(row["value_str"], style={
                            "padding": "5px 12px", "textAlign": "right",
                            "fontSize": "13px", "color": config.COLORS["text"],
                            "fontWeight": "500",
                        }),
                    ], style={
                        "backgroundColor": config.COLORS["table_row_alt"] if i % 2 == 0 else "transparent",
                    })
                    for i, (_, row) in enumerate(last10.iterrows())
                ]),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
        ]),
    ])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(
    Output("main-content", "children"),
    Output("last-data-date", "children"),
    Input("metric-dropdown", "value"),
    Input("interval-refresh", "n_intervals"),
)
def update_dashboard(metric_name, _n):
    all_data = data_module.get_all_data()

    if all_data is None:
        return setup_message(), "Not connected"

    # Most recent date across all current FY data
    current_fy = data_module.get_current_fy()
    cy_df = all_data.get(current_fy, pd.DataFrame())
    if not cy_df.empty and "date" in cy_df.columns:
        most_recent = cy_df["date"].max()
        date_str = fmt_date(most_recent)
    else:
        date_str = "No data"

    try:
        content = build_main_content(metric_name, all_data)
    except Exception as exc:
        content = html.Div(
            f"Error building dashboard: {exc}",
            style={"color": config.COLORS["negative"], "padding": "40px", "textAlign": "center"},
        )

    return content, date_str


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
