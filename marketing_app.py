"""
Marketing Command Centre - Priceline Pharmacy Pacific Fair.

Social media + SEO pipeline dashboard: schedule, tick-off tracking, calendar,
and playbook. Content plan lives in marketing_plan.py; progress is saved to
marketing_state.json (local only, gitignored).

Run with: python marketing_app.py
Then open http://localhost:8060  (POS dashboard stays on 8050)
"""
import json
import os
import calendar as pycal
from datetime import date, datetime, timedelta

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
from dash.exceptions import PreventUpdate

from marketing_plan import TASKS, PLAYBOOK, CHANNEL_COLORS, WEEKS

# Optional second lock for remote access (Cloudflare Access is the primary one).
# Set the MARKETING_PASSWORD environment variable to require a browser login;
# leave it unset for plain local use.
MARKETING_PASSWORD = os.environ.get("MARKETING_PASSWORD", "")

# ---------------------------------------------------------------------------
# Theme (matches the POS dashboard dark palette, with Priceline pink accent)
# ---------------------------------------------------------------------------
C = {
    "bg": "#1a1a2e", "card": "#16213e", "border": "#0f3460",
    "text": "#ffffff", "muted": "#a0a0b8", "pink": "#e6007e",
    "positive": "#00e676", "warn": "#ffb300", "negative": "#ff5252",
    "row_alt": "#1a1a3e",
}
FONT = "'Segoe UI', system-ui, -apple-system, sans-serif"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marketing_state.json")

PLAN_START = WEEKS[0]["start"]
PLAN_END = WEEKS[-1]["start"] + timedelta(days=6)


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def set_status(task_id, status):
    """status: 'done' | 'skipped' | None (toggle off)."""
    state = load_state()
    if status is None:
        state.pop(task_id, None)
    else:
        state[task_id] = {"status": status, "at": datetime.now().isoformat(timespec="minutes")}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    return state


def status_of(state, task_id):
    return state.get(task_id, {}).get("status")


TASK_BY_ID = {t["id"]: t for t in TASKS}


# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    title="Marketing Command Centre",
    update_title=None,
    assets_folder="marketing_assets",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

if MARKETING_PASSWORD:
    from flask import request, Response

    @server.before_request
    def _require_password():
        auth = request.authorization
        if not auth or auth.password != MARKETING_PASSWORD:
            return Response("Login required.", 401,
                            {"WWW-Authenticate": 'Basic realm="Marketing Command Centre"'})


# ---------------------------------------------------------------------------
# Small UI helpers
# ---------------------------------------------------------------------------
def chip(text, color, filled=False):
    return html.Span(text, style={
        "backgroundColor": color if filled else f"{color}33",
        "color": "#111" if filled else color,
        "border": f"1px solid {color}",
        "borderRadius": "20px", "padding": "1px 10px",
        "fontSize": "11px", "fontWeight": "600", "whiteSpace": "nowrap",
    })


def fmt_day(d):
    return d.strftime("%a %d %b")


def detail_block(label, text, copy_id=None):
    if not text:
        return None
    header_kids = [html.Span(label, style={
        "fontSize": "11px", "fontWeight": "700", "letterSpacing": "1px",
        "color": C["pink"], "textTransform": "uppercase"})]
    if copy_id:
        header_kids.append(dcc.Clipboard(
            target_id=copy_id, title="Copy",
            style={"display": "inline-block", "marginLeft": "8px",
                   "color": C["muted"], "cursor": "pointer", "fontSize": "14px"}))
    return html.Div([
        html.Div(header_kids, style={"marginBottom": "4px"}),
        html.Div(text, id=copy_id, style={
            "whiteSpace": "pre-wrap", "fontSize": "13px", "lineHeight": "1.55",
            "color": C["text"], "backgroundColor": C["bg"],
            "border": f"1px solid {C['border']}", "borderRadius": "8px",
            "padding": "10px 12px"}) if copy_id else
        html.Div(text, style={
            "whiteSpace": "pre-wrap", "fontSize": "13px", "lineHeight": "1.55",
            "color": C["text"], "backgroundColor": C["bg"],
            "border": f"1px solid {C['border']}", "borderRadius": "8px",
            "padding": "10px 12px"}),
    ], style={"marginTop": "10px"})


def task_card(t, state, highlight=False, show_date=False):
    st = status_of(state, t["id"])
    color = CHANNEL_COLORS.get(t["channel"], C["muted"])
    done, skipped = st == "done", st == "skipped"

    title_style = {"fontWeight": "600", "fontSize": "14px", "flex": "1", "minWidth": "180px"}
    if done or skipped:
        title_style.update({"textDecoration": "line-through", "color": C["muted"]})

    meta = [chip(t["channel"], color), chip(t["type"], C["muted"])]
    if show_date:
        meta.insert(0, chip(fmt_day(t["date"]), C["pink"]))
    if t["best_time"]:
        meta.append(html.Span(f"\U0001F552 {t['best_time']}", style={"color": C["muted"], "fontSize": "11px"}))
    meta.append(html.Span(f"~{t['mins']} min", style={"color": C["muted"], "fontSize": "11px"}))

    done_btn = html.Button(
        "✓ Done" if not done else "✓ Done!",
        id={"k": "act", "a": "done", "id": t["id"]}, n_clicks=0,
        style={"backgroundColor": C["positive"] if done else "transparent",
               "color": "#111" if done else C["positive"],
               "border": f"1.5px solid {C['positive']}", "borderRadius": "8px",
               "padding": "4px 14px", "cursor": "pointer", "fontWeight": "700",
               "fontSize": "12px", "fontFamily": FONT})
    skip_btn = html.Button(
        "Skipped" if skipped else "Skip",
        id={"k": "act", "a": "skip", "id": t["id"]}, n_clicks=0,
        style={"backgroundColor": C["warn"] if skipped else "transparent",
               "color": "#111" if skipped else C["muted"],
               "border": f"1px solid {C['warn'] if skipped else C['muted']}",
               "borderRadius": "8px", "padding": "4px 10px", "cursor": "pointer",
               "fontSize": "12px", "fontFamily": FONT})

    details_kids = [d for d in [
        detail_block("Copy / instructions", t["content"], copy_id=f"cp-{t['id']}"),
        detail_block("AI image prompt", t["image_prompt"], copy_id=f"ci-{t['id']}"),
        detail_block("AI video prompt", t["video_prompt"], copy_id=f"cv-{t['id']}"),
        detail_block("Photos to take", t["photo_brief"]),
        detail_block("Notes", t["notes"]),
    ] if d is not None]

    body = html.Details([
        html.Summary("Show content ▾", style={
            "cursor": "pointer", "color": C["muted"], "fontSize": "12px",
            "marginTop": "6px", "outline": "none"}),
        html.Div(details_kids),
    ]) if details_kids else None

    card_style = {
        "backgroundColor": C["card"], "borderRadius": "10px",
        "borderLeft": f"4px solid {color}",
        "border": f"1px solid {C['border']}",
        "borderLeftWidth": "4px", "borderLeftColor": color,
        "padding": "12px 14px", "marginBottom": "10px",
        "opacity": "0.55" if (done or skipped) else "1",
    }
    if highlight and not (done or skipped):
        card_style.update({"boxShadow": f"0 0 0 2px {C['pink']}", "position": "relative"})

    kids = []
    if highlight and not (done or skipped):
        kids.append(html.Div("▶ UP NEXT", style={
            "color": C["pink"], "fontWeight": "800", "fontSize": "10px",
            "letterSpacing": "2px", "marginBottom": "6px"}))
    kids.append(html.Div([
        html.Div(meta, style={"display": "flex", "gap": "8px", "alignItems": "center",
                              "flexWrap": "wrap", "marginBottom": "6px"}),
        html.Div([
            html.Div(t["title"], style=title_style),
            html.Div([done_btn, skip_btn], style={"display": "flex", "gap": "8px"}),
        ], style={"display": "flex", "gap": "12px", "alignItems": "center",
                  "flexWrap": "wrap", "justifyContent": "space-between"}),
    ]))
    if body is not None:
        kids.append(body)
    return html.Div(kids, style=card_style)


def section_header(text, color=None, sub=None):
    kids = [html.Span(text, style={
        "fontSize": "13px", "fontWeight": "800", "letterSpacing": "1.5px",
        "textTransform": "uppercase", "color": color or C["muted"]})]
    if sub:
        kids.append(html.Span(f"  {sub}", style={"fontSize": "12px", "color": C["muted"]}))
    return html.Div(kids, style={"margin": "18px 0 10px 2px"})


# ---------------------------------------------------------------------------
# Tab renderers
# ---------------------------------------------------------------------------
def render_today(state):
    today = date.today()
    overdue = [t for t in TASKS if t["date"] < today and not status_of(state, t["id"])]
    todays = [t for t in TASKS if t["date"] == today]
    upcoming = [t for t in TASKS if today < t["date"] <= today + timedelta(days=3)]

    kids = []
    first_pending_marked = False

    if overdue:
        kids.append(section_header(f"Catch-up — {len(overdue)} overdue", C["negative"],
                                   "oldest first: tick Done or Skip to clear the backlog"))
        for t in overdue:
            hl = not first_pending_marked
            kids.append(task_card(t, state, highlight=hl, show_date=True))
            first_pending_marked = True
    else:
        kids.append(html.Div("\U0001F389 All caught up — nothing overdue!", style={
            "backgroundColor": f"{C['positive']}18", "border": f"1px solid {C['positive']}",
            "borderRadius": "10px", "padding": "12px 16px", "color": C["positive"],
            "fontWeight": "600", "marginTop": "14px"}))

    kids.append(section_header(f"Today — {fmt_day(today)}", C["pink"]))
    if todays:
        for t in todays:
            hl = not first_pending_marked and not status_of(state, t["id"])
            kids.append(task_card(t, state, highlight=hl))
            if hl:
                first_pending_marked = True
    else:
        msg = "Nothing scheduled today — enjoy it!"
        if today > PLAN_END:
            msg = ("This 8-week plan has finished. Run the Monthly Review in the Playbook "
                   "and ask Claude to generate the next block.")
        elif today < PLAN_START:
            msg = f"Plan starts {fmt_day(PLAN_START)} — get ahead via the Pipeline tab."
        kids.append(html.Div(msg, style={"color": C["muted"], "padding": "6px 2px"}))

    if upcoming:
        kids.append(section_header("Coming up (next 3 days)", C["muted"]))
        for t in upcoming:
            kids.append(task_card(t, state, show_date=True))

    return html.Div(kids, style={"maxWidth": "860px", "margin": "0 auto"})


def render_calendar(state, month_str, sel_day):
    y, m = int(month_str[:4]), int(month_str[5:7])
    first = date(y, m, 1)
    today = date.today()

    nav = html.Div([
        html.Button("◀", id="cal-prev", n_clicks=0, style=_navbtn()),
        html.Div(first.strftime("%B %Y"), style={
            "fontSize": "18px", "fontWeight": "700", "minWidth": "170px",
            "textAlign": "center"}),
        html.Button("▶", id="cal-next", n_clicks=0, style=_navbtn()),
    ], style={"display": "flex", "gap": "14px", "alignItems": "center",
              "justifyContent": "center", "margin": "14px 0"})

    headers = [html.Div(d, style={
        "textAlign": "center", "fontSize": "11px", "fontWeight": "700",
        "color": C["muted"], "padding": "4px 0"}) for d in
        ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]]

    cells = []
    for wk in pycal.Calendar(firstweekday=0).monthdatescalendar(y, m):
        for d in wk:
            in_month = d.month == m
            day_tasks = [t for t in TASKS if t["date"] == d]
            chips = []
            for t in day_tasks[:4]:
                st = status_of(state, t["id"])
                col = CHANNEL_COLORS.get(t["channel"], C["muted"])
                chips.append(html.Div(t["type"], style={
                    "backgroundColor": f"{col}2e", "color": col,
                    "borderLeft": f"3px solid {col}", "borderRadius": "4px",
                    "fontSize": "9.5px", "padding": "1px 5px", "marginTop": "3px",
                    "overflow": "hidden", "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                    "textDecoration": "line-through" if st else "none",
                    "opacity": "0.5" if st else "1"}))
            if len(day_tasks) > 4:
                chips.append(html.Div(f"+{len(day_tasks) - 4} more", style={
                    "fontSize": "9px", "color": C["muted"], "marginTop": "2px"}))

            all_done = day_tasks and all(status_of(state, t["id"]) for t in day_tasks)
            style = {
                "backgroundColor": C["card"] if in_month else C["bg"],
                "border": f"1px solid {C['border']}",
                "borderRadius": "8px", "padding": "5px 6px", "minHeight": "84px",
                "cursor": "pointer" if day_tasks else "default",
                "opacity": "1" if in_month else "0.35",
            }
            if d == today:
                style["border"] = f"2px solid {C['pink']}"
            if sel_day == d.isoformat():
                style["boxShadow"] = f"0 0 0 2px {C['pink']}"

            num = html.Div([
                html.Span(str(d.day), style={"fontSize": "12px", "fontWeight": "700",
                                             "color": C["text"] if in_month else C["muted"]}),
                html.Span(" ✓" if all_done else "", style={"color": C["positive"], "fontSize": "11px"}),
            ])
            cells.append(html.Div([num] + chips,
                                  id={"k": "day", "d": d.isoformat()},
                                  n_clicks=0, style=style))

    grid = html.Div(headers + cells, style={
        "display": "grid", "gridTemplateColumns": "repeat(7, 1fr)",
        "gap": "6px"})

    panel = []
    if sel_day:
        sel = date.fromisoformat(sel_day)
        sel_tasks = [t for t in TASKS if t["date"] == sel]
        if sel_tasks:
            panel.append(section_header(f"{fmt_day(sel)} — {len(sel_tasks)} task(s)", C["pink"]))
            for t in sel_tasks:
                panel.append(task_card(t, state))

    legend = html.Div([chip(ch, col) for ch, col in CHANNEL_COLORS.items()],
                      style={"display": "flex", "gap": "8px", "flexWrap": "wrap",
                             "justifyContent": "center", "margin": "12px 0 4px"})

    return html.Div([nav, grid, legend, html.Div(panel)],
                    style={"maxWidth": "980px", "margin": "0 auto"})


def _navbtn():
    return {"backgroundColor": C["card"], "color": C["text"],
            "border": f"1px solid {C['border']}", "borderRadius": "8px",
            "padding": "4px 14px", "cursor": "pointer", "fontSize": "14px"}


def render_pipeline(state):
    today = date.today()
    kids = []
    for w in WEEKS:
        wstart, wend = w["start"], w["start"] + timedelta(days=6)
        wtasks = [t for t in TASKS if t.get("week") == w["num"]]
        ndone = sum(1 for t in wtasks if status_of(state, t["id"]))
        current = wstart <= today <= wend
        pct = int(ndone / len(wtasks) * 100) if wtasks else 0

        day_groups = []
        for offset in range(7):
            d = wstart + timedelta(days=offset)
            dts = [t for t in wtasks if t["date"] == d]
            if not dts:
                continue
            day_groups.append(html.Div(fmt_day(d), style={
                "fontSize": "12px", "fontWeight": "700", "color": C["muted"],
                "margin": "12px 0 6px 2px"}))
            day_groups.extend(task_card(t, state) for t in dts)

        summary = html.Summary([
            html.Span(f"Week {w['num']} — {w['theme']}", style={
                "fontWeight": "700", "fontSize": "15px"}),
            html.Span(f"  {wstart.strftime('%d %b')} – {wend.strftime('%d %b')}",
                      style={"color": C["muted"], "fontSize": "12px"}),
            html.Span("  ● THIS WEEK" if current else "", style={
                "color": C["pink"], "fontSize": "11px", "fontWeight": "800"}),
            html.Span(f"   {ndone}/{len(wtasks)} done ({pct}%)", style={
                "color": C["positive"] if pct == 100 else C["muted"],
                "fontSize": "12px", "float": "right"}),
        ], style={"cursor": "pointer", "padding": "12px 14px", "outline": "none",
                  "listStylePosition": "inside"})

        kids.append(html.Details([summary, html.Div(day_groups, style={
            "padding": "4px 14px 12px"})],
            open=current,
            style={"backgroundColor": C["card"], "borderRadius": "10px",
                   "border": f"1px solid {C['border']}",
                   "borderLeft": f"4px solid {C['pink'] if current else C['border']}",
                   "marginBottom": "10px"}))
    return html.Div(kids, style={"maxWidth": "900px", "margin": "0 auto"})


def render_playbook():
    cards = []
    for s in PLAYBOOK:
        cards.append(html.Div([
            html.Div(f"{s['icon']}  {s['title']}", style={
                "fontSize": "16px", "fontWeight": "700", "marginBottom": "8px",
                "color": C["pink"]}),
            dcc.Markdown(s["body"], style={
                "fontSize": "13.5px", "lineHeight": "1.6", "color": C["text"]}),
        ], style={"backgroundColor": C["card"], "borderRadius": "10px",
                  "border": f"1px solid {C['border']}", "padding": "16px 20px",
                  "marginBottom": "14px"}))
    return html.Div(cards, style={"maxWidth": "820px", "margin": "0 auto"})


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def default_month():
    today = date.today()
    if PLAN_START <= today <= PLAN_END:
        return today.strftime("%Y-%m")
    return PLAN_START.strftime("%Y-%m")


tab_style = {"backgroundColor": C["bg"], "color": C["muted"],
             "border": "none", "borderBottom": f"2px solid {C['border']}",
             "padding": "10px 18px", "fontWeight": "600", "fontFamily": FONT}
tab_sel = {**tab_style, "color": C["pink"],
           "borderBottom": f"2px solid {C['pink']}", "backgroundColor": C["bg"]}

app.layout = html.Div([
    dcc.Store(id="bump", data=0),
    dcc.Store(id="cal-month", data=default_month()),
    dcc.Store(id="sel-day", data=None),

    html.Div([
        html.Div([
            html.Div("MARKETING COMMAND CENTRE", style={
                "fontSize": "20px", "fontWeight": "800", "letterSpacing": "1px"}),
            html.Div("Priceline Pharmacy Pacific Fair — social & SEO pipeline", style={
                "fontSize": "12px", "color": C["muted"], "marginTop": "2px"}),
        ]),
        html.Div(id="hdr-progress", style={"textAlign": "right"}),
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "flexWrap": "wrap", "gap": "10px",
              "padding": "18px 24px", "borderBottom": f"3px solid {C['pink']}",
              "backgroundColor": C["card"]}),

    dcc.Tabs(id="tabs", value="today", children=[
        dcc.Tab(label="✅ Today", value="today", style=tab_style, selected_style=tab_sel),
        dcc.Tab(label="\U0001F4C5 Calendar", value="calendar", style=tab_style, selected_style=tab_sel),
        dcc.Tab(label="\U0001F5C2️ Pipeline", value="pipeline", style=tab_style, selected_style=tab_sel),
        dcc.Tab(label="\U0001F4D6 Playbook", value="playbook", style=tab_style, selected_style=tab_sel),
    ], style={"backgroundColor": C["bg"]}),

    html.Div(id="tab-content", style={"padding": "16px 20px 60px"}),
], style={"backgroundColor": C["bg"], "color": C["text"], "fontFamily": FONT,
          "minHeight": "100vh"})


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("bump", "data"),
              Input({"k": "act", "a": ALL, "id": ALL}, "n_clicks"),
              State("bump", "data"), prevent_initial_call=True)
def on_action(n_clicks, bump):
    trig = ctx.triggered_id
    if not trig or not ctx.triggered[0]["value"]:
        raise PreventUpdate
    task_id, action = trig["id"], trig["a"]
    if task_id not in TASK_BY_ID:
        raise PreventUpdate
    current = status_of(load_state(), task_id)
    if action == "done":
        set_status(task_id, None if current == "done" else "done")
    else:
        set_status(task_id, None if current == "skipped" else "skipped")
    return (bump or 0) + 1


@app.callback(Output("cal-month", "data"),
              Input("cal-prev", "n_clicks"), Input("cal-next", "n_clicks"),
              State("cal-month", "data"), prevent_initial_call=True)
def on_month_nav(_p, _n, month_str):
    if not ctx.triggered_id or not ctx.triggered[0]["value"]:
        raise PreventUpdate
    y, m = int(month_str[:4]), int(month_str[5:7])
    m += -1 if ctx.triggered_id == "cal-prev" else 1
    if m == 0:
        y, m = y - 1, 12
    elif m == 13:
        y, m = y + 1, 1
    return f"{y:04d}-{m:02d}"


@app.callback(Output("sel-day", "data"),
              Input({"k": "day", "d": ALL}, "n_clicks"),
              State("sel-day", "data"), prevent_initial_call=True)
def on_day_click(_clicks, current):
    trig = ctx.triggered_id
    if not trig or not ctx.triggered[0]["value"]:
        raise PreventUpdate
    d = trig["d"]
    return None if current == d else d


@app.callback(Output("tab-content", "children"),
              Input("tabs", "value"), Input("bump", "data"),
              Input("cal-month", "data"), Input("sel-day", "data"))
def render_tab(tab, _bump, month_str, sel_day):
    state = load_state()
    if tab == "calendar":
        return render_calendar(state, month_str or default_month(), sel_day)
    if tab == "pipeline":
        return render_pipeline(state)
    if tab == "playbook":
        return render_playbook()
    return render_today(state)


@app.callback(Output("hdr-progress", "children"), Input("bump", "data"))
def render_header(_bump):
    state = load_state()
    today = date.today()
    wstart = today - timedelta(days=today.weekday())
    week_tasks = [t for t in TASKS if wstart <= t["date"] <= wstart + timedelta(days=6)]
    scope, label = (week_tasks, "this week") if week_tasks else (TASKS, "overall")
    ndone = sum(1 for t in scope if status_of(state, t["id"]))
    pct = int(ndone / len(scope) * 100) if scope else 0
    overdue = sum(1 for t in TASKS if t["date"] < today and not status_of(state, t["id"]))

    bar = html.Div(html.Div(style={
        "width": f"{pct}%", "height": "8px", "backgroundColor": C["positive"] if pct else C["border"],
        "borderRadius": "4px", "transition": "width .3s"}),
        style={"width": "180px", "height": "8px", "backgroundColor": C["bg"],
               "borderRadius": "4px", "border": f"1px solid {C['border']}",
               "display": "inline-block", "verticalAlign": "middle"})

    kids = [html.Div([
        html.Span(f"{ndone}/{len(scope)} {label}  ", style={"fontSize": "12px", "color": C["muted"]}),
        bar,
        html.Span(f"  {pct}%", style={"fontSize": "13px", "fontWeight": "700",
                                      "color": C["positive"] if pct >= 70 else C["text"]}),
    ])]
    if overdue:
        kids.append(html.Div(f"⚠ {overdue} overdue — see Catch-up", style={
            "fontSize": "11px", "color": C["negative"], "fontWeight": "700",
            "marginTop": "3px"}))
    else:
        kids.append(html.Div("All caught up \U0001F389", style={
            "fontSize": "11px", "color": C["positive"], "marginTop": "3px"}))
    return kids


if __name__ == "__main__":
    print("Marketing Command Centre -> http://localhost:8060")
    try:
        from waitress import serve  # production server, ideal for always-on use
        serve(server, host="127.0.0.1", port=8060, threads=4)
    except ImportError:
        app.run(debug=False, port=8060)
