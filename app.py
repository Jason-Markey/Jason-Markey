"""
Pharmacy POS Dashboard — main application.
Run with: python app.py
Then open http://localhost:8050 in your browser.
"""
import os
import platform
from datetime import date, datetime, timedelta

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import config
import data as data_module
import holidays

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
    if fmt == "percentage":
        return f"{val:.1f}%"
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
        # Small differences (e.g. Average Sale) need cents to be visible
        if abs(val) < 100:
            return f"{arrow} ${abs(val):,.2f}", positive
        return f"{arrow} ${abs(val):,.0f}", positive
    if fmt == "number":
        return f"{arrow} {abs(val):,.0f}", positive
    if fmt == "number_2dp":
        return f"{arrow} {abs(val):,.2f}", positive
    if fmt == "percentage":
        return f"{arrow} {abs(val):.1f}pp", positive
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


def get_ytd_to_month(df: pd.DataFrame, agg: str, fy: str, max_month: int, max_day: int = None):
    """YTD for a prior year capped at the same FY month — and, if max_day is
    given, capped at the same day within that final month (true like-for-like)."""
    in_fy = df["fy_year"] == fy
    before_month = df["fy_month"] < max_month
    in_month = df["fy_month"] == max_month
    if max_day is not None:
        in_month = in_month & (df["date"].apply(lambda d: d.day) <= max_day)
    sub = df[in_fy & (before_month | in_month)]
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
        "borderRadius": "10px",
        "padding": "20px",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base, className="dash-card")


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


def add_holiday_markers(fig, start, end):
    """Dotted vertical lines + labels for QLD public holidays in the window."""
    for d, name in holidays.holidays_between(start, end).items():
        x = datetime(d.year, d.month, d.day)
        fig.add_vline(x=x, line=dict(color=config.COLORS["accent_light"], width=1, dash="dot"))
        fig.add_annotation(
            x=x, y=1, yref="paper", yanchor="bottom",
            text=name, showarrow=False, textangle=-38,
            font=dict(size=9, color=config.COLORS["text_muted"]),
        )
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
DROPDOWN_OPTIONS = []
for _group in config.METRIC_GROUPS:
    DROPDOWN_OPTIONS.append({
        "label": f"── {_group} ──", "value": f"__header_{_group}", "disabled": True,
    })
    for _name, _meta in config.METRICS.items():
        if _meta.get("group") == _group:
            DROPDOWN_OPTIONS.append({"label": f"    {_name}", "value": _name})

_LOGO_EXISTS = os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png"))

app.layout = html.Div(
    id="page-root",
    style={
        "backgroundColor": config.COLORS["background"],
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "color": config.COLORS["text"],
        "padding": "24px",
    },
    children=[
        dcc.Interval(id="interval-refresh", interval=config.CACHE_TTL * 1000, n_intervals=0),
        dcc.Store(id="theme-store", data="dark", storage_type="local"),

        # ── Header ──────────────────────────────────────────────────────────
        html.Div(id="app-header", children=[
            html.Div([
                html.Img(src="/assets/logo.png", style={
                    "height": "48px", "marginRight": "16px", "borderRadius": "6px",
                }) if _LOGO_EXISTS else None,
                html.Div([
                    html.H1(
                        "Priceline Pharmacy Pacific Fair",
                        style={"margin": "0", "fontSize": "26px", "fontWeight": "700"},
                    ),
                    html.Div("Point of Sale Summary", style={
                        "fontSize": "13px", "color": config.COLORS["text_muted"],
                        "letterSpacing": "1px", "textTransform": "uppercase",
                    }),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div([
                html.Button("☀ / 🌙", id="theme-toggle", n_clicks=0, title="Switch light/dark theme", style={
                    "backgroundColor": "transparent",
                    "color": config.COLORS["text_muted"],
                    "border": f"1px solid {config.COLORS['card_border']}",
                    "borderRadius": "6px",
                    "padding": "8px 12px",
                    "cursor": "pointer",
                    "marginRight": "12px",
                    "fontSize": "13px",
                }),
                html.Button("Refresh Now", id="refresh-button", n_clicks=0, style={
                    "backgroundColor": config.COLORS["accent"],
                    "color": "#ffffff",
                    "border": f"1px solid {config.COLORS['card_border']}",
                    "borderRadius": "6px",
                    "padding": "8px 16px",
                    "cursor": "pointer",
                    "marginRight": "16px",
                    "fontSize": "13px",
                }),
                html.Span("Most Recent Data From: ", style={"fontSize": "14px"}),
                html.Span(id="last-data-date", style={"fontWeight": "600", "fontSize": "14px"}),
                html.Span(id="last-refresh-time", style={"fontSize": "12px", "marginLeft": "16px"}),
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
                dcc.Tab(label="Month Detail", value="tab-month",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="FY Comparison", value="tab-year",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Trends", value="tab-trends",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Day of Week", value="tab-dow",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Custom Range", value="tab-range",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Monthly Report", value="tab-report",
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

        # ── Custom range picker (Custom Range tab only) ───────────────────
        html.Div([
            html.Label("Date Range", style={"color": config.COLORS["text_muted"],
                                            "fontSize": "13px", "marginBottom": "6px",
                                            "display": "block"}),
            dcc.DatePickerRange(
                id="date-range-picker",
                display_format="D/M/YYYY",
                start_date=(date.today() - timedelta(days=28)),
                end_date=date.today(),
                className="range-picker",
            ),
        ], id="range-container", style={"display": "none"}),

        # ── Report month picker (Monthly Report tab only) ─────────────────
        html.Div([
            html.Div([
                html.Label("Report Month", style={"color": config.COLORS["text_muted"],
                                                  "fontSize": "13px", "marginBottom": "6px",
                                                  "display": "block"}),
                dcc.Dropdown(
                    id="report-month-dropdown",
                    clearable=False,
                    style={"width": "240px", "maxWidth": "100%",
                           "color": "#000000", "backgroundColor": "#ffffff"},
                    className="metric-dropdown",
                ),
            ]),
            html.Button("Print / Save as PDF", id="print-button", n_clicks=0, style={
                "backgroundColor": config.COLORS["accent_light"],
                "color": config.COLORS["text"],
                "border": "none",
                "borderRadius": "6px",
                "padding": "10px 20px",
                "cursor": "pointer",
                "fontSize": "13px",
                "fontWeight": "600",
                "alignSelf": "flex-end",
            }),
        ], id="report-container", style={"display": "none"}),

        # ── Month picker (Month Detail tab only) ──────────────────────────
        html.Div([
            html.Label("Month", style={"color": config.COLORS["text_muted"],
                                       "fontSize": "13px", "marginBottom": "6px",
                                       "display": "block"}),
            dcc.Dropdown(
                id="month-detail-dropdown",
                clearable=False,
                style={"width": "240px", "maxWidth": "100%",
                       "color": "#000000", "backgroundColor": "#ffffff"},
                className="metric-dropdown",
            ),
        ], id="month-container", style={"display": "none"}),

        # ── Year picker (Day of Week tab only) ─────────────────────────────
        html.Div([
            html.Label("Years to Show", style={"color": config.COLORS["text_muted"],
                                               "fontSize": "13px", "marginBottom": "6px",
                                               "display": "block"}),
            dcc.Dropdown(
                id="dow-years-dropdown",
                multi=True,
                style={"width": "380px", "maxWidth": "100%",
                       "color": "#000000", "backgroundColor": "#ffffff"},
                className="metric-dropdown",
            ),
        ], id="dow-container", style={"display": "none"}),

        # ── Year pickers (Year in Review tab only) ────────────────────────
        html.Div([
            html.Div([
                html.Label("Year", style={"color": config.COLORS["text_muted"],
                                          "fontSize": "13px", "marginBottom": "6px",
                                          "display": "block"}),
                dcc.Dropdown(
                    id="year-a-dropdown",
                    clearable=False,
                    style={"width": "180px", "maxWidth": "100%",
                           "color": "#000000", "backgroundColor": "#ffffff"},
                    className="metric-dropdown",
                ),
            ]),
            html.Div([
                html.Label("Compare Against", style={"color": config.COLORS["text_muted"],
                                                     "fontSize": "13px", "marginBottom": "6px",
                                                     "display": "block"}),
                dcc.Dropdown(
                    id="year-b-dropdown",
                    clearable=False,
                    style={"width": "180px", "maxWidth": "100%",
                           "color": "#000000", "backgroundColor": "#ffffff"},
                    className="metric-dropdown",
                ),
            ]),
            html.Button("Print / Save as PDF", id="year-print-button", n_clicks=0, style={
                "backgroundColor": config.COLORS["accent_light"],
                "color": config.COLORS["text"],
                "border": "none",
                "borderRadius": "6px",
                "padding": "10px 20px",
                "cursor": "pointer",
                "fontSize": "13px",
                "fontWeight": "600",
                "alignSelf": "flex-end",
            }),
        ], id="year-container", style={"display": "none"}),

        html.Div(id="main-content"),
        html.Div(id="print-dummy", style={"display": "none"}),
        html.Div(id="print-dummy-2", style={"display": "none"}),
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

    def sparkline(metric_df):
        """Tiny 90-day trend line (weekly totals to smooth noise)."""
        cutoff = date.today() - timedelta(days=90)
        sub = metric_df[metric_df["date"] >= cutoff].sort_values("date")
        if len(sub) < 7:
            return None
        s = sub.set_index("date")["value"].rolling(7, min_periods=4).mean().dropna()
        if s.empty:
            return None
        fig = go.Figure(go.Scatter(
            x=list(s.index), y=list(s.values), mode="lines",
            line=dict(color=config.COLORS["line_cy"], width=1.5),
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=2, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            showlegend=False, height=42,
        )
        return dcc.Graph(figure=fig, config={"staticPlot": True},
                         style={"height": "42px", "marginTop": "8px"})

    def metric_card(metric_name, meta):
        key = meta["key"]
        fmt = meta["format"]
        agg = meta["aggregation"]
        metric_df = data_module.get_metric_data(all_data, key)

        # Cap prior years at this metric's most recent uploaded date, not today
        cy_dates = metric_df[metric_df["fy_year"] == current_fy]["date"]
        ref_date = cy_dates.max() if not cy_dates.empty else today
        ref_fy_month = data_module.get_fy_month(ref_date)

        ytd_cy = get_ytd(metric_df, agg, current_fy)
        ytd_py = get_ytd_to_month(metric_df, agg, prior_fy, ref_fy_month, ref_date.day) if prior_fy else None
        pct = None
        if ytd_cy is not None and ytd_py and ytd_py != 0:
            pct = (ytd_cy - ytd_py) / ytd_py * 100
        pct_str, pct_pos = fmt_pct(pct)

        return card([
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
            sparkline(metric_df),
        ], style={"flex": "1 1 200px", "minWidth": "180px", "padding": "16px"})

    sections = [
        html.Div(f"Year to Date ({current_fy}) — all metrics vs same point last year", style={
            "fontSize": "13px", "color": config.COLORS["text_muted"],
            "marginBottom": "16px",
        }),
    ]
    for group in config.METRIC_GROUPS:
        group_cards = [
            metric_card(name, meta)
            for name, meta in config.METRICS.items()
            if meta.get("group") == group
        ]
        if not group_cards:
            continue
        sections.append(html.Div(group, style={
            "fontSize": "15px", "fontWeight": "700", "color": config.COLORS["text"],
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "margin": "20px 0 12px 0", "paddingBottom": "6px",
            "borderBottom": f"2px solid {config.COLORS['accent_light']}",
        }))
        sections.append(html.Div(group_cards, style={
            "display": "flex", "flexWrap": "wrap", "gap": "14px",
        }))

    return html.Div(sections)


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
    three_yr_fy = data_module.get_prior_fy(current_fy, 3)

    metric_df = data_module.get_metric_data(all_data, key)

    today = date.today()
    # Cap prior years at the most recent uploaded date for this metric, not today
    cy_dates = metric_df[metric_df["fy_year"] == current_fy]["date"]
    ref_date = cy_dates.max() if not cy_dates.empty else today
    current_fy_month = data_module.get_fy_month(ref_date)

    # ── YTD values ────────────────────────────────────────────────────────
    ytd_cy = get_ytd(metric_df, agg, current_fy)
    ytd_py = get_ytd_to_month(metric_df, agg, prior_fy, current_fy_month, ref_date.day) if prior_fy else None
    ytd_2yr = get_ytd_to_month(metric_df, agg, two_yr_fy, current_fy_month, ref_date.day) if two_yr_fy else None
    ytd_3yr = get_ytd_to_month(metric_df, agg, three_yr_fy, current_fy_month, ref_date.day) if three_yr_fy else None

    diff_py = (ytd_cy - ytd_py) if (ytd_cy is not None and ytd_py is not None) else None
    diff_2yr = (ytd_cy - ytd_2yr) if (ytd_cy is not None and ytd_2yr is not None) else None
    diff_3yr = (ytd_cy - ytd_3yr) if (ytd_cy is not None and ytd_3yr is not None) else None
    pct_py = (diff_py / ytd_py * 100) if (diff_py is not None and ytd_py and ytd_py != 0) else None
    pct_2yr = (diff_2yr / ytd_2yr * 100) if (diff_2yr is not None and ytd_2yr and ytd_2yr != 0) else None
    pct_3yr = (diff_3yr / ytd_3yr * 100) if (diff_3yr is not None and ytd_3yr and ytd_3yr != 0) else None

    diff_py_str, diff_py_pos = fmt_diff(diff_py, fmt)
    diff_2yr_str, diff_2yr_pos = fmt_diff(diff_2yr, fmt)
    diff_3yr_str, diff_3yr_pos = fmt_diff(diff_3yr, fmt)
    pct_py_str, pct_py_pos = fmt_pct(pct_py)
    pct_2yr_str, pct_2yr_pos = fmt_pct(pct_2yr)
    pct_3yr_str, pct_3yr_pos = fmt_pct(pct_3yr)

    # ── MTD values (current month vs same month PY, capped at same day) ──
    max_day = ref_date.day
    mtd_cy = get_mtd(metric_df, agg, current_fy, current_fy_month)
    mtd_py = get_mtd(metric_df, agg, prior_fy, current_fy_month, max_day) if prior_fy else None
    mtd_2yr = get_mtd(metric_df, agg, two_yr_fy, current_fy_month, max_day) if two_yr_fy else None
    mtd_3yr = get_mtd(metric_df, agg, three_yr_fy, current_fy_month, max_day) if three_yr_fy else None

    mtd_diff_py = (mtd_cy - mtd_py) if (mtd_cy is not None and mtd_py is not None) else None
    mtd_diff_2yr = (mtd_cy - mtd_2yr) if (mtd_cy is not None and mtd_2yr is not None) else None
    mtd_diff_3yr = (mtd_cy - mtd_3yr) if (mtd_cy is not None and mtd_3yr is not None) else None
    mtd_pct_py = (mtd_diff_py / mtd_py * 100) if (mtd_diff_py is not None and mtd_py and mtd_py != 0) else None
    mtd_pct_2yr = (mtd_diff_2yr / mtd_2yr * 100) if (mtd_diff_2yr is not None and mtd_2yr and mtd_2yr != 0) else None
    mtd_pct_3yr = (mtd_diff_3yr / mtd_3yr * 100) if (mtd_diff_3yr is not None and mtd_3yr and mtd_3yr != 0) else None

    mtd_diff_py_str, mtd_diff_py_pos = fmt_diff(mtd_diff_py, fmt)
    mtd_diff_2yr_str, mtd_diff_2yr_pos = fmt_diff(mtd_diff_2yr, fmt)
    mtd_diff_3yr_str, mtd_diff_3yr_pos = fmt_diff(mtd_diff_3yr, fmt)
    mtd_pct_py_str, mtd_pct_py_pos = fmt_pct(mtd_pct_py)
    mtd_pct_2yr_str, mtd_pct_2yr_pos = fmt_pct(mtd_pct_2yr)
    mtd_pct_3yr_str, mtd_pct_3yr_pos = fmt_pct(mtd_pct_3yr)

    month_name = ref_date.strftime("%B")

    # ── Last 10 days ──────────────────────────────────────────────────────
    cy_df = metric_df[metric_df["fy_year"] == current_fy].sort_values("date", ascending=False)
    last10 = cy_df.head(10)[["date", "value"]].copy()
    last10["date_str"] = last10["date"].apply(fmt_date)
    last10["value_str"] = last10["value"].apply(lambda v: fmt_value(v, fmt))

    # ── Monthly aggregates ────────────────────────────────────────────────
    cy_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == current_fy], agg)
    py_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == prior_fy], agg) if prior_fy else pd.Series(dtype=float)
    twoyr_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == two_yr_fy], agg) if two_yr_fy else pd.Series(dtype=float)
    threeyr_monthly = aggregate_monthly(metric_df[metric_df["fy_year"] == three_yr_fy], agg) if three_yr_fy else pd.Series(dtype=float)

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
    if three_yr_fy and not threeyr_monthly.empty:
        fig.add_trace(go.Scatter(
            x=MONTH_LABELS,
            y=[safe_get(threeyr_monthly, m) for m in months],
            mode="lines+markers", name=three_yr_fy,
            line=dict(color=config.COLORS["line_3yr"], width=2),
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
    diffs_3yr = diff_vals(cy_monthly, threeyr_monthly)
    pcts_py = pct_vals(diffs_py, py_monthly)
    pcts_2yr = pct_vals(diffs_2yr, twoyr_monthly)
    pcts_3yr = pct_vals(diffs_3yr, threeyr_monthly)

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
        "-3 Yr": row_vals(threeyr_monthly),
        "vs PY": arrow_fmt(diffs_py),
        "vs -2yr": arrow_fmt(diffs_2yr),
        "vs -3yr": arrow_fmt(diffs_3yr),
        "vs PY%": arrow_fmt(pcts_py, is_pct=True),
        "vs -2yr%": arrow_fmt(pcts_2yr, is_pct=True),
        "vs -3yr%": arrow_fmt(pcts_3yr, is_pct=True),
    }
    color_map = {
        "vs PY": color_cells(diffs_py),
        "vs -2yr": color_cells(diffs_2yr),
        "vs -3yr": color_cells(diffs_3yr),
        "vs PY%": color_cells(pcts_py),
        "vs -2yr%": color_cells(pcts_2yr),
        "vs -3yr%": color_cells(pcts_3yr),
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
                comparison_line(f"vs {three_yr_fy} YTD" if three_yr_fy else "vs -3yr",
                                diff_3yr_str, diff_3yr_pos, pct_3yr_str, pct_3yr_pos),
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
                comparison_line(f"vs {three_yr_fy} MTD" if three_yr_fy else "vs -3yr",
                                mtd_diff_3yr_str, mtd_diff_3yr_pos, mtd_pct_3yr_str, mtd_pct_3yr_pos),
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
            html.Div(
                f"Note: {month_name} is part-complete, so its column compares against the "
                "full month last year. The YTD cards above are like-for-like (prior years "
                "cut off at the same day).",
                style={"fontSize": "11px", "color": config.COLORS["text_muted"], "marginTop": "8px"},
            ),
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

    # Optional target reference line (set in config.TARGETS)
    target = config.TARGETS.get(metric_name)
    if target:
        fig.add_hline(
            y=target,
            line=dict(color=config.COLORS["positive"], width=1.5, dash="dash"),
            annotation_text=f"Target {fmt_value(target, meta['format'])}",
            annotation_font=dict(color=config.COLORS["positive"], size=11),
        )

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

    # ── Script type mix (% of dispensary dollars by category, monthly) ──────
    mix_section = []
    mix_keys = [
        ("Concession", "concession"), ("General", "general"),
        ("Entitlement", "entitlement"), ("Safety Net", "safety_net"),
        ("Private", "private_disp"), ("Repat", "repat"),
    ]
    mix_colors = [config.COLORS["line_cy"], config.COLORS["line_py"],
                  config.COLORS["line_2yr"], config.COLORS["accent_light"],
                  config.COLORS["positive"], config.COLORS["text_muted"]]
    mix_cutoff = date.today() - timedelta(days=425)
    fig3 = go.Figure()
    has_mix = False
    for (label, mkey), colr in zip(mix_keys, mix_colors):
        mdf = data_module.get_metric_data(all_data, mkey)
        mdf = mdf[mdf["date"] >= mix_cutoff]
        if mdf.empty:
            continue
        has_mix = True
        s = mdf.set_index(pd.to_datetime(mdf["date"]))["value"].resample("MS").sum()
        fig3.add_trace(go.Bar(x=list(s.index), y=list(s.values), name=label,
                              marker_color=colr))
    if has_mix:
        dark_chart_layout(fig3, title="Script Type Mix — share of dispensary $ by month")
        fig3.update_layout(barmode="stack", barnorm="percent", hovermode="x unified")
        fig3.update_yaxes(ticksuffix="%", tickformat=".0f")
        mix_section = [card([
            dcc.Graph(figure=fig3, config=GRAPH_CONFIG, style={"height": "380px"}),
            html.Div(
                "Shows how the dispensary mix (concession / general / private etc.) is shifting over time.",
                style={"fontSize": "12px", "color": config.COLORS["text_muted"], "marginTop": "8px"},
            ),
        ], style={"marginTop": "24px"})]

    return html.Div([
        card([
            dcc.Graph(figure=fig, config=GRAPH_CONFIG, style={"height": "380px"}),
        ], style={"marginBottom": "24px"}),
    ] + corr_section + mix_section)


# ---------------------------------------------------------------------------
# Day of Week tab
# ---------------------------------------------------------------------------
def build_dow(metric_name: str, all_data: dict, selected_fys=None):
    meta = config.METRICS[metric_name]
    key = meta["key"]
    fmt = meta["format"]

    current_fy = data_module.get_current_fy()
    prior_fy = data_module.get_prior_fy(current_fy, 1)

    metric_df = data_module.get_metric_data(all_data, key)
    if metric_df.empty:
        return html.Div("No data available.", style={"color": config.COLORS["text_muted"]})

    if not selected_fys:
        selected_fys = [fy for fy in (current_fy, prior_fy) if fy]
    # Plot oldest first so newest ends up drawn last / rightmost in each group
    selected_fys = sorted(set(selected_fys), key=lambda f: int(f.split("/")[0]))

    def weekday_means(fy):
        sub = metric_df[metric_df["fy_year"] == fy].copy()
        if sub.empty:
            return [None] * 7
        sub["weekday"] = sub["date"].apply(lambda d: d.weekday())
        means = sub.groupby("weekday")["value"].mean()
        return [means.get(i, None) for i in range(7)]

    bar_colors = [config.COLORS["line_3yr"], config.COLORS["line_2yr"],
                  config.COLORS["line_py"], config.COLORS["line_cy"]]
    # Newest year always gets the CY colour, working backwards for older years
    n = len(selected_fys)
    colors_for = bar_colors[-n:] if n <= len(bar_colors) else bar_colors * ((n // len(bar_colors)) + 1)

    fig = go.Figure()
    for fy_label, colr in zip(selected_fys, colors_for):
        fig.add_trace(go.Bar(
            x=WEEKDAY_LABELS, y=weekday_means(fy_label), name=fy_label,
            marker_color=colr,
        ))
    dark_chart_layout(fig, title=f"{metric_name} — Average by Day of Week")
    fig.update_layout(barmode="group", hovermode="x")

    cy_means = weekday_means(selected_fys[-1])

    # Best / worst day callout
    valid = [(WEEKDAY_LABELS[i], v) for i, v in enumerate(cy_means) if v is not None]
    callout = []
    if valid:
        best = max(valid, key=lambda t: t[1])
        worst = min(valid, key=lambda t: t[1])
        callout = [html.Div([
            html.Span(f"Best day ({selected_fys[-1]}): ", style={"color": config.COLORS["text_muted"], "fontSize": "13px"}),
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
# Custom Range tab
# ---------------------------------------------------------------------------
def _shift_year(d, years):
    try:
        return d.replace(year=d.year - years)
    except ValueError:  # Feb 29
        return d.replace(year=d.year - years, day=28)


def build_range(metric_name: str, all_data: dict, start, end):
    meta = config.METRICS[metric_name]
    key = meta["key"]
    fmt = meta["format"]
    agg = meta["aggregation"]

    if isinstance(start, str):
        start = date.fromisoformat(start[:10])
    if isinstance(end, str):
        end = date.fromisoformat(end[:10])

    metric_df = data_module.get_metric_data(all_data, key)
    if metric_df.empty:
        return html.Div("No data available.", style={"color": config.COLORS["text_muted"]})

    def range_value(s, e):
        sub = metric_df[(metric_df["date"] >= s) & (metric_df["date"] <= e)]
        if sub.empty:
            return None, sub
        if agg == "average":
            return sub["value"].mean(), sub
        return sub["value"].sum(), sub

    val_cy, sub_cy = range_value(start, end)
    py_start, py_end = _shift_year(start, 1), _shift_year(end, 1)
    val_py, sub_py = range_value(py_start, py_end)
    two_start, two_end = _shift_year(start, 2), _shift_year(end, 2)
    val_2yr, sub_2yr = range_value(two_start, two_end)

    diff = (val_cy - val_py) if (val_cy is not None and val_py is not None) else None
    pct = (diff / val_py * 100) if (diff is not None and val_py and val_py != 0) else None
    diff_str, diff_pos = fmt_diff(diff, fmt)
    pct_str, pct_pos = fmt_pct(pct)

    diff2 = (val_cy - val_2yr) if (val_cy is not None and val_2yr is not None) else None
    pct2 = (diff2 / val_2yr * 100) if (diff2 is not None and val_2yr and val_2yr != 0) else None
    diff2_str, diff2_pos = fmt_diff(diff2, fmt)
    pct2_str, pct2_pos = fmt_pct(pct2)

    # Daily chart for the selected range, with the same range last year overlaid
    fig = go.Figure()
    if not sub_cy.empty:
        s = sub_cy.sort_values("date")
        fig.add_trace(go.Scatter(
            x=list(s["date"]), y=list(s["value"]),
            mode="lines+markers", name="Selected range",
            line=dict(color=config.COLORS["line_cy"], width=2.5), marker=dict(size=5),
        ))
    if not sub_py.empty:
        p = sub_py.sort_values("date").copy()
        # shift PY dates forward a year so the lines overlap on the same axis
        p["date_aligned"] = p["date"].apply(lambda d: _shift_year(d, -1))
        fig.add_trace(go.Scatter(
            x=list(p["date_aligned"]), y=list(p["value"]),
            mode="lines+markers", name="Same dates last year",
            line=dict(color=config.COLORS["line_py"], width=2, dash="dot"), marker=dict(size=4),
        ))
    if not sub_2yr.empty:
        p2 = sub_2yr.sort_values("date").copy()
        p2["date_aligned"] = p2["date"].apply(lambda d: _shift_year(d, -2))
        fig.add_trace(go.Scatter(
            x=list(p2["date_aligned"]), y=list(p2["value"]),
            mode="lines+markers", name="Same dates 2 years ago",
            line=dict(color=config.COLORS["line_2yr"], width=2, dash="dot"), marker=dict(size=4),
        ))
    dark_chart_layout(fig, title=f"{metric_name} — {fmt_date(start)} to {fmt_date(end)}")
    add_holiday_markers(fig, start, end)

    label = "Average" if agg == "average" else "Total"
    return html.Div([
        html.Div([
            card([
                html.Div(f"{label} for selected range", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"], "marginBottom": "8px",
                }),
                html.Div(fmt_value(val_cy, fmt), style={
                    "fontSize": "32px", "fontWeight": "700",
                    "color": config.COLORS["text"], "marginBottom": "12px",
                }),
                html.Hr(style={"borderColor": config.COLORS["card_border"], "margin": "12px 0"}),
                comparison_line(
                    f"vs {fmt_date(py_start)}–{fmt_date(py_end)}",
                    diff_str, diff_pos, pct_str, pct_pos,
                ),
                comparison_line(
                    f"vs {fmt_date(two_start)}–{fmt_date(two_end)}",
                    diff2_str, diff2_pos, pct2_str, pct2_pos,
                ),
                html.Div(f"Last year: {fmt_value(val_py, fmt)}", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"],
                }),
                html.Div(f"Two years ago: {fmt_value(val_2yr, fmt)}", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"],
                }),
            ], style={"flex": "1 1 300px", "minWidth": "280px"}),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "24px"}),
        card([
            dcc.Graph(figure=fig, config=GRAPH_CONFIG, style={"height": "380px"}),
        ]),
    ])


# ---------------------------------------------------------------------------
# Month Detail tab — one month, days across the x-axis, year over year
# ---------------------------------------------------------------------------
def build_month_detail(metric_name: str, all_data: dict, month_value: str):
    if not month_value:
        return html.Div("Select a month.", style={"color": config.COLORS["text_muted"]})

    meta = config.METRICS[metric_name]
    key = meta["key"]
    fmt = meta["format"]
    agg = meta["aggregation"]

    fy, m = month_value.split("|")
    m = int(m)
    prior_fy = data_module.get_prior_fy(fy, 1)
    two_yr_fy = data_module.get_prior_fy(fy, 2)
    three_yr_fy = data_module.get_prior_fy(fy, 3)

    month_label = MONTH_LABELS[m - 1]
    start_yy = int(fy.split("/")[0])
    year = 2000 + start_yy + (0 if m <= (12 - config.FY_START_MONTH + 1) else 1)
    cal_month = (m + config.FY_START_MONTH - 2) % 12 + 1

    metric_df = data_module.get_metric_data(all_data, key)
    if metric_df.empty:
        return html.Div("No data available.", style={"color": config.COLORS["text_muted"]})

    def month_days(fy_label):
        """Series indexed by day-of-month for one FY's month."""
        if not fy_label:
            return pd.Series(dtype=float)
        sub = metric_df[(metric_df["fy_year"] == fy_label) & (metric_df["fy_month"] == m)].copy()
        if sub.empty:
            return pd.Series(dtype=float)
        sub["day"] = sub["date"].apply(lambda d: d.day)
        return sub.sort_values("day").set_index("day")["value"]

    cy_days = month_days(fy)
    py_days = month_days(prior_fy)
    twoyr_days = month_days(two_yr_fy)
    threeyr_days = month_days(three_yr_fy)

    days = list(range(1, 32))

    def y_for(series):
        return [series.get(d, None) for d in days]

    # ── Daily line chart ────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=y_for(cy_days), mode="lines+markers", name=fy,
        line=dict(color=config.COLORS["line_cy"], width=2.5),
        marker=dict(size=6), connectgaps=False,
    ))
    if prior_fy and not py_days.empty:
        fig.add_trace(go.Scatter(
            x=days, y=y_for(py_days), mode="lines+markers", name=prior_fy,
            line=dict(color=config.COLORS["line_py"], width=2),
            marker=dict(size=5), connectgaps=False,
        ))
    if two_yr_fy and not twoyr_days.empty:
        fig.add_trace(go.Scatter(
            x=days, y=y_for(twoyr_days), mode="lines+markers", name=two_yr_fy,
            line=dict(color=config.COLORS["line_2yr"], width=2),
            marker=dict(size=5), connectgaps=False,
        ))
    if three_yr_fy and not threeyr_days.empty:
        fig.add_trace(go.Scatter(
            x=days, y=y_for(threeyr_days), mode="lines+markers", name=three_yr_fy,
            line=dict(color=config.COLORS["line_3yr"], width=2),
            marker=dict(size=5), connectgaps=False,
        ))
    dark_chart_layout(fig, title=f"{metric_name} — {month_label} {year} by day")
    fig.update_xaxes(dtick=1, title_text="Day of month")

    # ── Cumulative chart (sum metrics only) ─────────────────────────────
    cumulative_card = []
    if agg == "sum":
        fig2 = go.Figure()
        for label, series, colr, width in [
            (fy, cy_days, config.COLORS["line_cy"], 2.5),
            (prior_fy, py_days, config.COLORS["line_py"], 2),
            (two_yr_fy, twoyr_days, config.COLORS["line_2yr"], 2),
            (three_yr_fy, threeyr_days, config.COLORS["line_3yr"], 2),
        ]:
            if not label or series.empty:
                continue
            cum = series.sort_index().cumsum()
            fig2.add_trace(go.Scatter(
                x=list(cum.index), y=list(cum.values), mode="lines", name=label,
                line=dict(color=colr, width=width),
            ))
        dark_chart_layout(fig2, title=f"{metric_name} — {month_label} running total")
        fig2.update_xaxes(dtick=2, title_text="Day of month")
        cumulative_card = [card([
            dcc.Graph(figure=fig2, config=GRAPH_CONFIG, style={"height": "340px"}),
        ], style={"marginBottom": "24px"})]

    # ── Summary card ────────────────────────────────────────────────────
    def month_total(series):
        if series.empty:
            return None
        return series.mean() if agg == "average" else series.sum()

    v_cy, v_py = month_total(cy_days), month_total(py_days)
    diff = (v_cy - v_py) if (v_cy is not None and v_py is not None) else None
    pct = (diff / v_py * 100) if (diff is not None and v_py and v_py != 0) else None
    diff_str, diff_pos = fmt_diff(diff, fmt)
    pct_str, pct_pos = fmt_pct(pct)
    label = "Average" if agg == "average" else "Total"

    return html.Div([
        html.Div([
            card([
                html.Div(f"{metric_name} — {month_label} {year} {label.lower()}", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"], "marginBottom": "8px",
                }),
                html.Div(fmt_value(v_cy, fmt), style={
                    "fontSize": "32px", "fontWeight": "700",
                    "color": config.COLORS["text"], "marginBottom": "12px",
                }),
                html.Hr(style={"borderColor": config.COLORS["card_border"], "margin": "12px 0"}),
                comparison_line(f"vs {month_label} {prior_fy}" if prior_fy else "vs PY",
                                diff_str, diff_pos, pct_str, pct_pos),
                html.Div(f"Last year: {fmt_value(v_py, fmt)}", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"],
                }),
            ], style={"flex": "1 1 300px", "minWidth": "280px"}),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "24px"}),
        card([
            dcc.Graph(figure=fig, config=GRAPH_CONFIG, style={"height": "400px"}),
        ], style={"marginBottom": "24px"}),
    ] + cumulative_card)


# ---------------------------------------------------------------------------
# Monthly Report tab
# ---------------------------------------------------------------------------
def get_report_month_options(all_data: dict):
    """All (FY, fy_month) pairs that have data, newest first, as dropdown options."""
    seen = set()
    for fy, df in all_data.items():
        if df.empty:
            continue
        for _, row in df[["fy_year", "fy_month"]].drop_duplicates().iterrows():
            seen.add((row["fy_year"], int(row["fy_month"])))

    def sort_key(item):
        fy, m = item
        return (int(fy.split("/")[0]), m)

    options = []
    for fy, m in sorted(seen, key=sort_key, reverse=True):
        cal_month = (m + config.FY_START_MONTH - 2) % 12 + 1
        start_yy = int(fy.split("/")[0])
        year = 2000 + start_yy + (0 if m <= (12 - config.FY_START_MONTH + 1) else 1)
        label = f"{MONTH_LABELS[m - 1]} {year}"
        options.append({"label": label, "value": f"{fy}|{m}"})
    return options


def build_report(all_data: dict, report_value: str):
    if not report_value:
        return html.Div("Select a month.", style={"color": config.COLORS["text_muted"]})

    fy, m = report_value.split("|")
    m = int(m)
    prior_fy = data_module.get_prior_fy(fy, 1)

    month_label = MONTH_LABELS[m - 1]
    start_yy = int(fy.split("/")[0])
    year = 2000 + start_yy + (0 if m <= (12 - config.FY_START_MONTH + 1) else 1)

    header_style = {
        "padding": "10px 14px", "textAlign": "right",
        "backgroundColor": config.COLORS["table_header"],
        "color": config.COLORS["text"], "fontSize": "13px", "fontWeight": "600",
    }
    rows = [html.Tr([
        html.Th("Metric", style={**header_style, "textAlign": "left"}),
        html.Th(fy, style=header_style),
        html.Th(prior_fy or "PY", style=header_style),
        html.Th("Change", style=header_style),
        html.Th("Change %", style=header_style),
    ])]

    for metric_name, meta in config.METRICS.items():
        key = meta["key"]
        fmt = meta["format"]
        agg = meta["aggregation"]
        metric_df = data_module.get_metric_data(all_data, key)

        def month_value(fy_label):
            if not fy_label:
                return None
            sub = metric_df[(metric_df["fy_year"] == fy_label) & (metric_df["fy_month"] == m)]
            if sub.empty:
                return None
            return sub["value"].mean() if agg == "average" else sub["value"].sum()

        v_cy = month_value(fy)
        v_py = month_value(prior_fy)
        diff = (v_cy - v_py) if (v_cy is not None and v_py is not None) else None
        pct = (diff / v_py * 100) if (diff is not None and v_py and v_py != 0) else None

        diff_str, diff_pos = fmt_diff(diff, fmt)
        pct_str, pct_pos = fmt_pct(pct)
        diff_color = config.COLORS["positive"] if diff_pos else config.COLORS["negative"]
        pct_color = config.COLORS["positive"] if pct_pos else config.COLORS["negative"]
        if diff is None:
            diff_color = pct_color = config.COLORS["text_muted"]

        cell = {"padding": "9px 14px", "textAlign": "right", "fontSize": "13px",
                "borderBottom": f"1px solid {config.COLORS['card_border']}"}
        rows.append(html.Tr([
            html.Td(metric_name, style={**cell, "textAlign": "left",
                                        "color": config.COLORS["text"], "fontWeight": "500"}),
            html.Td(fmt_value(v_cy, fmt), style={**cell, "color": config.COLORS["text"]}),
            html.Td(fmt_value(v_py, fmt), style={**cell, "color": config.COLORS["text_muted"]}),
            html.Td(diff_str, style={**cell, "color": diff_color, "fontWeight": "600"}),
            html.Td(pct_str, style={**cell, "color": pct_color, "fontWeight": "600"}),
        ]))

    return html.Div([
        card([
            html.Div([
                html.H2(f"Monthly Report — {month_label} {year}", style={
                    "margin": "0 0 4px 0", "fontSize": "22px", "color": config.COLORS["text"],
                }),
                html.Div("Priceline Pharmacy Pacific Fair", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"], "marginBottom": "16px",
                }),
            ]),
            html.Div([
                html.Table(rows, style={"width": "100%", "borderCollapse": "collapse"}),
            ], style={"overflowX": "auto"}),
            html.Div(f"Generated {fmt_date(date.today())}", style={
                "fontSize": "11px", "color": config.COLORS["text_muted"], "marginTop": "16px",
            }),
        ]),
    ], id="report-printable")


# ---------------------------------------------------------------------------
# Year in Review tab
# ---------------------------------------------------------------------------
def get_fy_options(all_data: dict):
    """All financial years present in the data, newest first."""
    fys = [fy for fy, df in all_data.items() if not df.empty]
    fys.sort(key=lambda f: int(f.split("/")[0]), reverse=True)
    return [{"label": f"FY {fy}", "value": fy} for fy in fys]


def build_year_review(all_data: dict, fy_a: str, fy_b: str):
    if not fy_a or not fy_b:
        return html.Div("Select two years to compare.", style={"color": config.COLORS["text_muted"]})

    # Like-for-like: if the newer year is incomplete, cap the older year at
    # the newer year's most recent date (same FY month + day).
    def fy_dates(fy):
        df = all_data.get(fy, pd.DataFrame())
        if df.empty or "date" not in df.columns:
            return None
        return df["date"].max()

    newer_fy = max(fy_a, fy_b, key=lambda f: int(f.split("/")[0]))
    newer_max = fy_dates(newer_fy)
    current_fy = data_module.get_current_fy()
    partial = newer_fy == current_fy and newer_max is not None
    cap_month = data_module.get_fy_month(newer_max) if partial else None
    cap_day = newer_max.day if partial else None

    header_style = {
        "padding": "10px 14px", "textAlign": "right",
        "backgroundColor": config.COLORS["table_header"],
        "color": config.COLORS["text"], "fontSize": "13px", "fontWeight": "600",
    }
    rows = [html.Tr([
        html.Th("Metric", style={**header_style, "textAlign": "left"}),
        html.Th(f"FY {fy_a}", style=header_style),
        html.Th(f"FY {fy_b}", style=header_style),
        html.Th("Change", style=header_style),
        html.Th("Change %", style=header_style),
    ])]

    def group_header(group):
        return html.Tr([html.Td(group, colSpan=5, style={
            "padding": "12px 14px 6px 14px", "fontWeight": "700",
            "color": config.COLORS["text"], "fontSize": "13px",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "borderBottom": f"2px solid {config.COLORS['accent_light']}",
        })])

    def year_value(metric_df, agg, fy):
        sub = metric_df[metric_df["fy_year"] == fy]
        # Cap at same point in year when comparing a partial year
        if partial and fy != newer_fy and not sub.empty:
            in_month = (sub["fy_month"] == cap_month) & (sub["date"].apply(lambda d: d.day) <= cap_day)
            sub = sub[(sub["fy_month"] < cap_month) | in_month]
        if sub.empty:
            return None
        return sub["value"].mean() if agg == "average" else sub["value"].sum()

    for group in config.METRIC_GROUPS:
        group_metrics = [(n, m) for n, m in config.METRICS.items() if m.get("group") == group]
        if not group_metrics:
            continue
        rows.append(group_header(group))
        for metric_name, meta in group_metrics:
            key = meta["key"]
            fmt = meta["format"]
            agg = meta["aggregation"]
            metric_df = data_module.get_metric_data(all_data, key)

            v_a = year_value(metric_df, agg, fy_a)
            v_b = year_value(metric_df, agg, fy_b)
            diff = (v_a - v_b) if (v_a is not None and v_b is not None) else None
            pct = (diff / v_b * 100) if (diff is not None and v_b and v_b != 0) else None

            diff_str, diff_pos = fmt_diff(diff, fmt)
            pct_str, pct_pos = fmt_pct(pct)
            diff_color = config.COLORS["positive"] if diff_pos else config.COLORS["negative"]
            pct_color = config.COLORS["positive"] if pct_pos else config.COLORS["negative"]
            if diff is None:
                diff_color = pct_color = config.COLORS["text_muted"]

            cell = {"padding": "9px 14px", "textAlign": "right", "fontSize": "13px",
                    "borderBottom": f"1px solid {config.COLORS['card_border']}"}
            rows.append(html.Tr([
                html.Td(metric_name, style={**cell, "textAlign": "left",
                                            "color": config.COLORS["text"], "fontWeight": "500"}),
                html.Td(fmt_value(v_a, fmt), style={**cell, "color": config.COLORS["text"]}),
                html.Td(fmt_value(v_b, fmt), style={**cell, "color": config.COLORS["text_muted"]}),
                html.Td(diff_str, style={**cell, "color": diff_color, "fontWeight": "600"}),
                html.Td(pct_str, style={**cell, "color": pct_color, "fontWeight": "600"}),
            ]))

    note = ""
    if partial:
        note = (f"Note: FY {newer_fy} is in progress (data to {fmt_date(newer_max)}). "
                f"The other year is capped at the same point for a like-for-like comparison.")

    return html.Div([
        card([
            html.Div([
                html.H2(f"FY Comparison — FY {fy_a} vs FY {fy_b}", style={
                    "margin": "0 0 4px 0", "fontSize": "22px", "color": config.COLORS["text"],
                }),
                html.Div("Priceline Pharmacy Pacific Fair", style={
                    "fontSize": "13px", "color": config.COLORS["text_muted"], "marginBottom": "16px",
                }),
            ]),
            html.Div([
                html.Table(rows, style={"width": "100%", "borderCollapse": "collapse"}),
            ], style={"overflowX": "auto"}),
            html.Div(note, style={
                "fontSize": "11px", "color": config.COLORS["text_muted"], "marginTop": "12px",
            }) if note else None,
        ]),
    ], id="report-printable")


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(
    Output("theme-store", "data"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(_clicks, current):
    return "light" if current == "dark" else "dark"


@app.callback(
    Output("main-content", "children"),
    Output("last-data-date", "children"),
    Output("last-refresh-time", "children"),
    Output("dropdown-container", "style"),
    Output("range-container", "style"),
    Output("report-container", "style"),
    Output("report-month-dropdown", "options"),
    Output("report-month-dropdown", "value"),
    Output("month-container", "style"),
    Output("month-detail-dropdown", "options"),
    Output("month-detail-dropdown", "value"),
    Output("year-container", "style"),
    Output("year-a-dropdown", "options"),
    Output("year-a-dropdown", "value"),
    Output("year-b-dropdown", "options"),
    Output("year-b-dropdown", "value"),
    Output("dow-container", "style"),
    Output("dow-years-dropdown", "options"),
    Output("dow-years-dropdown", "value"),
    Output("page-root", "style"),
    Output("page-root", "className"),
    Input("main-tabs", "value"),
    Input("metric-dropdown", "value"),
    Input("interval-refresh", "n_intervals"),
    Input("refresh-button", "n_clicks"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("report-month-dropdown", "value"),
    Input("month-detail-dropdown", "value"),
    Input("year-a-dropdown", "value"),
    Input("year-b-dropdown", "value"),
    Input("dow-years-dropdown", "value"),
    Input("theme-store", "data"),
)
def update_dashboard(tab, metric_name, _n, _clicks, range_start, range_end,
                     report_value, month_value, year_a, year_b, dow_years, theme):
    ctx = dash.callback_context
    force = bool(ctx.triggered and ctx.triggered[0]["prop_id"].startswith("refresh-button"))

    # Apply theme palette before building any content
    config.COLORS = config.PALETTES.get(theme, config.PALETTES["dark"])
    root_style = {
        "backgroundColor": config.COLORS["background"],
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "color": config.COLORS["text"],
        "padding": "24px",
    }
    root_class = "theme-light" if theme == "light" else "theme-dark"

    all_data = data_module.get_all_data(force_refresh=force)

    hidden = {"display": "none"}
    dropdown_style = {"marginBottom": "24px"}
    if tab in ("tab-overview", "tab-report", "tab-year"):
        dropdown_style = hidden
    range_style = {"marginBottom": "24px"} if tab == "tab-range" else hidden
    report_style = ({"marginBottom": "24px", "display": "flex", "gap": "20px",
                     "flexWrap": "wrap", "alignItems": "flex-end"}
                    if tab == "tab-report" else hidden)
    month_style = {"marginBottom": "24px"} if tab == "tab-month" else hidden
    year_style = ({"marginBottom": "24px", "display": "flex", "gap": "20px",
                   "flexWrap": "wrap", "alignItems": "flex-end"}
                  if tab == "tab-year" else hidden)
    dow_style = {"marginBottom": "24px"} if tab == "tab-dow" else hidden

    if all_data is None:
        return (setup_message(), "Not connected", "", dropdown_style,
                range_style, report_style, [], None,
                month_style, [], None,
                year_style, [], None, [], None,
                dow_style, [], None, root_style, root_class)

    report_options = get_report_month_options(all_data)
    if report_value is None and report_options:
        report_value = report_options[0]["value"]
    if month_value is None and report_options:
        month_value = report_options[0]["value"]

    fy_options = get_fy_options(all_data)
    if year_a is None and fy_options:
        year_a = fy_options[0]["value"]
    if year_b is None and len(fy_options) > 1:
        year_b = fy_options[1]["value"]
    elif year_b is None and fy_options:
        year_b = fy_options[0]["value"]

    if not dow_years and fy_options:
        dow_years = [o["value"] for o in fy_options[:2]]

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
            content = build_dow(metric_name, all_data, dow_years)
        elif tab == "tab-range":
            content = build_range(metric_name, all_data, range_start, range_end)
        elif tab == "tab-report":
            content = build_report(all_data, report_value)
        elif tab == "tab-month":
            content = build_month_detail(metric_name, all_data, month_value)
        elif tab == "tab-year":
            content = build_year_review(all_data, year_a, year_b)
        else:
            content = build_detail(metric_name, all_data)
    except Exception as exc:
        content = html.Div(
            f"Error building dashboard: {exc}",
            style={"color": config.COLORS["negative"], "padding": "40px", "textAlign": "center"},
        )

    return (content, date_str, refresh_str, dropdown_style,
            range_style, report_style, report_options, report_value,
            month_style, report_options, month_value,
            year_style, fy_options, year_a, fy_options, year_b,
            dow_style, fy_options, dow_years,
            root_style, root_class)


# Browser print dialog (lets the user save the report as a PDF)
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) { window.print(); }
        return "";
    }
    """,
    Output("print-dummy", "children"),
    Input("print-button", "n_clicks"),
    prevent_initial_call=True,
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) { window.print(); }
        return "";
    }
    """,
    Output("print-dummy-2", "children"),
    Input("year-print-button", "n_clicks"),
    prevent_initial_call=True,
)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
