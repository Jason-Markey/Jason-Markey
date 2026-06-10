"""
Pharmacy POS Dashboard — main application.
Run with: python app.py
Then open http://localhost:8050 in your browser.
"""
import platform
from datetime import date, datetime, timedelta

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # for gunicorn if needed

GRAPH_CONFIG = {
    "displayModeBar": True,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d",
        "autoScale2d", "resetScale2d",
    ],
    "toImageButtonOptions": {"format": "png", "filename": "pharmacy-dashboard", "scale": 2},
    "displaylogo": False,
}

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


def fmt_value_short(val, fmt: str) -> str:
    """Compact format for overview cards."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if fmt == "currency":
        if abs(val) >= 1_000_000:
            return f"${val / 1_000_000:,.2f}M"
        if abs(val) >= 10_000:
            return f"${val / 1_000:,.0f}K"
        return f"${val:,.0f}"
    if fmt == "number":
        return f"{val:,.0f}"
    if fmt == "number_2dp":
        return f"{val:,.2f}"
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
WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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


def get_mtd(df: pd.DataFrame, agg: str, fy: str, fy_month: int, max_day: int = None):
    """Month-to-date for a given FY month, optionally capped at a day of month."""
    sub = df[(df["fy_year"] == fy) & (df["fy_month"] == fy_month)]
    if max_day is not None:
        sub = sub[sub["date"].apply(lambda d: d.day) <= max_day]
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


def comparison_line(label, diff_str, diff_pos, pct_str, pct_pos):
    return html.Div([
        html.Span(f"{label}  ", style={"fontSize": "13px", "color": config.COLORS["text_muted"]}),
        html.Span(diff_str, style={
            "fontSize": "14px", "fontWeight": "600", "marginRight": "10px",
            "color": config.COLORS["positive"] if diff_pos else config.COLORS["negative"],
        }),
        html.Span(pct_str, style={
            "fontSize": "14px", "fontWeight": "600",
            "color": config.COLORS["positive"] if pct_pos else config.COLORS["negative"],
        }),
    ], style={"marginBottom": "8px"})


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


def dark_chart_layout(fig, title=None, height=None):
    fig.update_layout(
        plot_bgcolor=config.COLORS["card"],
        paper_bgcolor=config.COLORS["card"],
        font=dict(color=config.COLORS["text"], size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(color=config.COLORS["text"]),
        ),
        xaxis=dict(gridcolor="#2a2a4a", showline=True, linecolor=config.COLORS["card_border"]),
        yaxis=dict(gridcolor="#2a2a4a", showline=True, linecolor=config.COLORS["card_border"],
                   tickformat=",.0f"),
        margin=dict(l=60, r=20, t=50, b=40),
        hovermode="x unified",
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=16, color=config.COLORS["text"])))
    return fig


TAB_STYLE = {
    "backgroundColor": config.COLORS["card"],
    "color": config.COLORS["text_muted"],
    "border": f"1px solid {config.COLORS['card_border']}",
    "padding": "10px 18px",
    "fontSize": "14px",
}
TAB_SELECTED_STYLE = {
    "backgroundColor": config.COLORS["accent"],
    "color": config.COLORS["text"],
    "border": f"1px solid {config.COLORS['card_border']}",
    "padding": "10px 18px",
    "fontSize": "14px",
    "fontWeight": "600",
}

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
        dcc.Interval(id="interval-refresh", interval=config.CACHE_TTL * 1000, n_intervals=0),

        # ── Header ──────────────────────────────────────────────────────────
        html.Div([
            html.H1(
                "Point of Sale Summary",
                style={"margin": "0", "fontSize": "28px", "fontWeight": "700",
                       "color": config.COLORS["text"]},
            ),
            html.Div([
                html.Button("Refresh Now", id="refresh-button", n_clicks=0, style={
                    "backgroundColor": config.COLORS["accent"],
                    "color": config.COLORS["text"],
                    "border": f"1px solid {config.COLORS['card_border']}",
                    "borderRadius": "6px",
                    "padding": "8px 16px",
                    "cursor": "pointer",
                    "marginRight": "16px",
                    "fontSize": "13px",
                }),
                html.Span("Most Recent Data From: ", style={"color": config.COLORS["text_muted"],
                                                             "fontSize": "14px"}),
                html.Span(id="last-data-date", style={"color": config.COLORS["accent_light"],
                                                       "fontWeight": "600", "fontSize": "14px"}),
                html.Span(id="last-refresh-time", style={"color": config.COLORS["text_muted"],
                                                          "fontSize": "12px", "marginLeft": "16px"}),
            ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap"}),
        ], style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "flexWrap": "wrap",
            "gap": "12px",
            "marginBottom": "20px",
            "paddingBottom": "16px",
            "borderBottom": f"1px solid {config.COLORS['card_border']}",
        }),

        # ── Tabs ──────────────────────────────────────────────────────────────
        dcc.Tabs(
            id="main-tabs",
            value="tab-overview",
            children=[
                dcc.Tab(label="Overview", value="tab-overview",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Metric Detail", value="tab-detail",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Trends", value="tab-trends",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Day of Week", value="tab-dow",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
            ],
            style={"marginBottom": "20px"},
        ),

        # ── Metric dropdown (used by Detail / Trends / Day of Week tabs) ─────
        html.Div([
            html.Label("View By", style={"color": config.COLORS["text_muted"],
                                          "fontSize": "13px", "marginBottom": "6px",
                                          "display": "block"}),
            dcc.Dropdown(
                id="metric-dropdown",
                options=DROPDOWN_OPTIONS,
                value="Daily Sales",
                clearable=False,
                style={
                    "width": "320px",
                    "maxWidth": "100%",
                    "color": "#000000",
                    "backgroundColor": "#ffffff",
                },
                className="metric-dropdown",
            ),
        ], id="dropdown-container", style={"marginBottom": "24px"}),

        html.Div(id="main-content"),
    ],
)


# ---------------------------------------------------------------------------
# Overview tab
# ---------------------------------------------------------------------------
def build_overview(all_data: dict):
    current_fy = data_module.get_current_fy()
    prior_fy = data_module.get_prior_fy(current_fy, 1)
    today = date.today()
    current_fy_month = data_module.get_fy_month(today)

    cards = []
    for metric_name, meta in config.METRICS.items():
        key = meta["key"]
        fmt = meta["format"]
        agg = meta["aggregation"]
        metric_df = data_module.get_metric_data(all_data, key)

        ytd_cy = get_ytd(metric_df, agg, current_fy)
        ytd_py = get_ytd_to_month(metric_df, agg, prior_fy, current_fy_month) if prior_fy else None
        pct = None
        if ytd_cy is not None and ytd_py and ytd_py != 0:
            pct = (ytd_cy - ytd_py) / ytd_py * 100
        pct_str, pct_pos = fmt_pct(pct)

        cards.append(card([
            html.Div(metric_name, style={
                "fontSize": "12px", "color": config.COLORS["text_muted"],
                "marginBottom": "6px", "minHeight": "30px",
            }),
            html.Div(fmt_value_short(ytd_cy, fmt), style={
                "fontSize": "24px", "fontWeight": "700",
                "color": config.COLORS["text"], "marginBottom": "6px",
            }),
            html.Div([
                html.Span("vs PY ", style={"fontSize": "11px", "color": config.COLORS["text_muted"]}),
                html.Span(pct_str, style={
                    "fontSize": "13px", "fontWeight": "600",
                    "color": config.COLORS["positive"] if pct_pos else config.COLORS["negative"],
                }),
            ]),
        ], style={"flex": "1 1 200px", "minWidth": "180px", "padding": "16px"}))

    return html.Div([
        html.Div(f"Year to Date ({current_fy}) — all metrics vs same point last year", style={
            "fontSize": "13px", "color": config.COLORS["text_muted"],
            "marginBottom": "16px",
        }),
        html.Div(cards, style={
            "display": "flex", "flexWrap": "wrap", "gap": "14px",
        }),
    ])


# ---------------------------------------------------------------------------
# Metric Detail tab
# ---------------------------------------------------------------------------
def build_detail(metric_name: str, all_data: dict):
    meta = config.METRICS[metric_name]
    key = meta["key"]
    fmt = meta["format"]
    agg = meta["aggregation"]

    current_fy = data_module.get_current_fy()
    prior_fy = data_module.get_prior_fy(current_fy, 1)
    two_yr_fy = data_module.get_prior_fy(current_fy, 2)

    metric_df = data_module.get_metric_data(all_data, key)

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

    # ── MTD values (current month vs same month PY, capped at same day) ──
    max_day = today.day
    mtd_cy = get_mtd(metric_df, agg, current_fy, current_fy_month)
    mtd_py = get_mtd(metric_df, agg, prior_fy, current_fy_month, max_day) if prior_fy else None
    mtd_2yr = get_mtd(metric_df, agg, two_yr_fy, current_fy_month, max_day) if two_yr_fy else None

    mtd_diff_py = (mtd_cy - mtd_py) if (mtd_cy is not None and mtd_py is not None) else None
    mtd_diff_2yr = (mtd_cy - mtd_2yr) if (mtd_cy is not None and mtd_2yr is not None) else None
    mtd_pct_py = (mtd_diff_py / mtd_py * 100) if (mtd_diff_py is not None and mtd_py and mtd_py != 0) else None
    mtd_pct_2yr = (mtd_diff_2yr / mtd_2yr * 100) if (mtd_diff_2yr is not None and mtd_2yr and mtd_2yr != 0) else None

    mtd_diff_py_str, mtd_diff_py_pos = fmt_diff(mtd_diff_py, fmt)
    mtd_diff_2yr_str, mtd_diff_2yr_pos = fmt_diff(mtd_diff_2yr, fmt)
    mtd_pct_py_str, mtd_pct_py_pos = fmt_pct(mtd_pct_py)
    mtd_pct_2yr_str, mtd_pct_2yr_pos = fmt_pct(mtd_pct_2yr)

    month_name = today.strftime("%B")

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
        mode="lines+markers", name=current_fy,
        line=dict(color=config.COLORS["line_cy"], width=2.5),
        marker=dict(size=6), connectgaps=False,
    ))
    if prior_fy:
        fig.add_trace(go.Scatter(
            x=MONTH_LABELS,
            y=[safe_get(py_monthly, m) for m in months],
            mode="lines+markers", name=prior_fy,
            line=dict(color=config.COLORS["line_py"], width=2),
            marker=dict(size=5), connectgaps=False,
        ))
    if two_yr_fy:
        fig.add_trace(go.Scatter(
            x=MONTH_LABELS,
            y=[safe_get(twoyr_monthly, m) for m in months],
            mode="lines+markers", name=two_yr_fy,
            line=dict(color=config.COLORS["line_2yr"], width=2),
            marker=dict(size=5), connectgaps=False,
        ))
    dark_chart_layout(fig, title=metric_name)

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

    def color_cells(vals):
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
        table_rows_html.append(make_table_row(row_label, vals, color_map.get(row_label)))

    # ── Assemble layout ───────────────────────────────────────────────────
    return html.Div([
        # YTD + MTD cards
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
                comparison_line(f"vs {prior_fy} YTD", diff_py_str, diff_py_pos, pct_py_str, pct_py_pos),
                comparison_line(f"vs {two_yr_fy} YTD" if two_yr_fy else "vs -2yr",
                                diff_2yr_str, diff_2yr_pos, pct_2yr_str, pct_2yr_pos),
            ], style={"flex": "1 1 300px", "minWidth": "280px"}),

            card([
                html.Div(f"{month_name} Month to Date", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"],
                    "marginBottom": "8px", "fontStyle": "italic",
                }),
                html.Div(fmt_value(mtd_cy, fmt), style={
                    "fontSize": "32px", "fontWeight": "700",
                    "color": config.COLORS["text"], "marginBottom": "16px",
                }),
                html.Div("MTD (prior years capped at same day of month)", style={
                    "fontSize": "11px", "color": config.COLORS["text_muted"],
                    "marginBottom": "12px", "textTransform": "uppercase",
                    "letterSpacing": "1px",
                }),
                html.Hr(style={"borderColor": config.COLORS["card_border"], "margin": "12px 0"}),
                comparison_line(f"vs {prior_fy} MTD", mtd_diff_py_str, mtd_diff_py_pos,
                                mtd_pct_py_str, mtd_pct_py_pos),
                comparison_line(f"vs {two_yr_fy} MTD" if two_yr_fy else "vs -2yr",
                                mtd_diff_2yr_str, mtd_diff_2yr_pos, mtd_pct_2yr_str, mtd_pct_2yr_pos),
            ], style={"flex": "1 1 300px", "minWidth": "280px"}),

        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "24px"}),

        # Line chart
        card([
            dcc.Graph(figure=fig, config=GRAPH_CONFIG, style={"height": "380px"}),
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

        # Last 10 days
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
# Trends tab
# ---------------------------------------------------------------------------
def build_trends(metric_name: str, all_data: dict):
    meta = config.METRICS[metric_name]
    key = meta["key"]

    metric_df = data_module.get_metric_data(all_data, key)
    if metric_df.empty:
        return html.Div("No data available.", style={"color": config.COLORS["text_muted"]})

    df = metric_df.sort_values("date").copy()
    # Limit to the last 14 months so the chart stays readable
    cutoff = date.today() - timedelta(days=425)
    df = df[df["date"] >= cutoff]
    df = df.set_index("date")

    daily = df["value"]
    roll7 = daily.rolling(7, min_periods=4).mean()
    roll28 = daily.rolling(28, min_periods=14).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(daily.index), y=list(daily.values),
        mode="markers", name="Daily",
        marker=dict(size=4, color=config.COLORS["text_muted"], opacity=0.45),
    ))
    fig.add_trace(go.Scatter(
        x=list(roll7.index), y=list(roll7.values),
        mode="lines", name="7-day average",
        line=dict(color=config.COLORS["line_cy"], width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=list(roll28.index), y=list(roll28.values),
        mode="lines", name="28-day average",
        line=dict(color=config.COLORS["line_py"], width=2.5),
    ))
    dark_chart_layout(fig, title=f"{metric_name} — Rolling Trend (last 14 months)")

    # ── Scripts vs Front Shop correlation (only shown once, on Trends tab) ──
    scripts_df = data_module.get_metric_data(all_data, "script_nos")
    sales_df = data_module.get_metric_data(all_data, "tax_sales")

    corr_section = []
    if not scripts_df.empty and not sales_df.empty:
        s = scripts_df.set_index("date")["value"].sort_index()
        f = sales_df.set_index("date")["value"].sort_index()
        s28 = s.rolling(28, min_periods=14).mean()
        f28 = f.rolling(28, min_periods=14).mean()

        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Scatter(
            x=list(s28.index), y=list(s28.values),
            mode="lines", name="Scripts (28-day avg)",
            line=dict(color=config.COLORS["line_2yr"], width=2.5),
        ), secondary_y=False)
        fig2.add_trace(go.Scatter(
            x=list(f28.index), y=list(f28.values),
            mode="lines", name="Front Shop Sales (28-day avg)",
            line=dict(color=config.COLORS["line_cy"], width=2.5),
        ), secondary_y=True)
        dark_chart_layout(fig2, title="Dispensary Scripts vs Front Shop Sales")
        fig2.update_yaxes(title_text="Scripts / day", secondary_y=False,
                          gridcolor="#2a2a4a", color=config.COLORS["text"])
        fig2.update_yaxes(title_text="Front Shop $ / day", secondary_y=True,
                          showgrid=False, color=config.COLORS["text"])

        corr_section = [card([
            dcc.Graph(figure=fig2, config=GRAPH_CONFIG, style={"height": "380px"}),
            html.Div(
                "If the lines move together, dispensary traffic is flowing through to front shop sales.",
                style={"fontSize": "12px", "color": config.COLORS["text_muted"], "marginTop": "8px"},
            ),
        ])]

    return html.Div([
        card([
            dcc.Graph(figure=fig, config=GRAPH_CONFIG, style={"height": "380px"}),
        ], style={"marginBottom": "24px"}),
    ] + corr_section)


# ---------------------------------------------------------------------------
# Day of Week tab
# ---------------------------------------------------------------------------
def build_dow(metric_name: str, all_data: dict):
    meta = config.METRICS[metric_name]
    key = meta["key"]
    fmt = meta["format"]

    current_fy = data_module.get_current_fy()
    prior_fy = data_module.get_prior_fy(current_fy, 1)

    metric_df = data_module.get_metric_data(all_data, key)
    if metric_df.empty:
        return html.Div("No data available.", style={"color": config.COLORS["text_muted"]})

    def weekday_means(fy):
        sub = metric_df[metric_df["fy_year"] == fy].copy()
        if sub.empty:
            return [None] * 7
        sub["weekday"] = sub["date"].apply(lambda d: d.weekday())
        means = sub.groupby("weekday")["value"].mean()
        return [means.get(i, None) for i in range(7)]

    cy_means = weekday_means(current_fy)
    py_means = weekday_means(prior_fy) if prior_fy else [None] * 7

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=WEEKDAY_LABELS, y=cy_means, name=current_fy,
        marker_color=config.COLORS["line_cy"],
    ))
    if prior_fy:
        fig.add_trace(go.Bar(
            x=WEEKDAY_LABELS, y=py_means, name=prior_fy,
            marker_color=config.COLORS["line_py"],
        ))
    dark_chart_layout(fig, title=f"{metric_name} — Average by Day of Week")
    fig.update_layout(barmode="group", hovermode="x")

    # Best / worst day callout
    valid = [(WEEKDAY_LABELS[i], v) for i, v in enumerate(cy_means) if v is not None]
    callout = []
    if valid:
        best = max(valid, key=lambda t: t[1])
        worst = min(valid, key=lambda t: t[1])
        callout = [html.Div([
            html.Span("Best day this year: ", style={"color": config.COLORS["text_muted"], "fontSize": "13px"}),
            html.Span(f"{best[0]} ({fmt_value(best[1], fmt)} avg)", style={
                "color": config.COLORS["positive"], "fontWeight": "600", "fontSize": "13px",
                "marginRight": "24px",
            }),
            html.Span("Quietest day: ", style={"color": config.COLORS["text_muted"], "fontSize": "13px"}),
            html.Span(f"{worst[0]} ({fmt_value(worst[1], fmt)} avg)", style={
                "color": config.COLORS["negative"], "fontWeight": "600", "fontSize": "13px",
            }),
        ], style={"marginTop": "12px"})]

    return card([
        dcc.Graph(figure=fig, config=GRAPH_CONFIG, style={"height": "400px"}),
    ] + callout)


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(
    Output("main-content", "children"),
    Output("last-data-date", "children"),
    Output("last-refresh-time", "children"),
    Output("dropdown-container", "style"),
    Input("main-tabs", "value"),
    Input("metric-dropdown", "value"),
    Input("interval-refresh", "n_intervals"),
    Input("refresh-button", "n_clicks"),
)
def update_dashboard(tab, metric_name, _n, _clicks):
    ctx = dash.callback_context
    force = bool(ctx.triggered and ctx.triggered[0]["prop_id"].startswith("refresh-button"))

    all_data = data_module.get_all_data(force_refresh=force)

    dropdown_style = {"marginBottom": "24px"}
    if tab == "tab-overview":
        dropdown_style["display"] = "none"

    if all_data is None:
        return setup_message(), "Not connected", "", dropdown_style

    current_fy = data_module.get_current_fy()
    cy_df = all_data.get(current_fy, pd.DataFrame())
    if not cy_df.empty and "date" in cy_df.columns:
        date_str = fmt_date(cy_df["date"].max())
    else:
        date_str = "No data"

    refresh_str = f"Refreshed {datetime.now().strftime('%H:%M')}"

    try:
        if tab == "tab-overview":
            content = build_overview(all_data)
        elif tab == "tab-trends":
            content = build_trends(metric_name, all_data)
        elif tab == "tab-dow":
            content = build_dow(metric_name, all_data)
        else:
            content = build_detail(metric_name, all_data)
    except Exception as exc:
        content = html.Div(
            f"Error building dashboard: {exc}",
            style={"color": config.COLORS["negative"], "padding": "40px", "textAlign": "center"},
        )

    return content, date_str, refresh_str, dropdown_style


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
