"""
Email summary report for Pharmacy POS Dashboard.

Usage:
    python email_report.py weekly    — last full week (Mon-Sun) vs same week last year
    python email_report.py monthly   — last full calendar month vs same month last year

Requires:
    ~/.pharmacy-dashboard/resend_key.txt   (Resend API key)
    ~/.pharmacy-dashboard/credentials.json (Google service account)
"""
import os
import sys
import json
import urllib.request
from datetime import date, timedelta

import config
import data as data_module

RESEND_KEY_FILE = os.path.join(os.path.expanduser("~"), ".pharmacy-dashboard", "resend_key.txt")
TO_EMAIL = "jason@pricelinepf.com.au"
FROM_EMAIL = "onboarding@resend.dev"  # Resend's default sender (no domain setup needed)

POSITIVE = "#1a7d3c"
NEGATIVE = "#b00020"
MUTED = "#888888"


def fmt_value(val, fmt):
    if val is None:
        return "—"
    if fmt == "currency":
        return f"${val:,.2f}"
    if fmt == "number":
        return f"{val:,.0f}"
    if fmt == "number_2dp":
        return f"{val:,.2f}"
    if fmt == "percentage":
        return f"{val:.1f}%"
    return str(val)


def shift_year(d, years=1):
    try:
        return d.replace(year=d.year - years)
    except ValueError:  # Feb 29
        return d.replace(year=d.year - years, day=28)


def get_period(mode):
    """Return (start, end, label) for the last full week or month."""
    today = data_module.today()
    if mode == "weekly":
        # Last full Mon-Sun week
        last_sunday = today - timedelta(days=today.weekday() + 1)
        start = last_sunday - timedelta(days=6)
        return start, last_sunday, f"Week {start.strftime('%d/%m')} – {last_sunday.strftime('%d/%m/%Y')}"
    # Last full calendar month
    first_of_this_month = today.replace(day=1)
    end = first_of_this_month - timedelta(days=1)
    start = end.replace(day=1)
    return start, end, end.strftime("%B %Y")


def build_summary(all_data, start, end):
    """Return list of (metric_name, cy_str, py_str, pct, fmt) rows."""
    rows = []
    py_start, py_end = shift_year(start), shift_year(end)
    for metric_name, meta in config.METRICS.items():
        key = meta["key"]
        fmt = meta["format"]
        agg = meta["aggregation"]
        df = data_module.get_metric_data(all_data, key)

        def period_value(s, e):
            sub = df[(df["date"] >= s) & (df["date"] <= e)]
            if sub.empty:
                return None
            return sub["value"].mean() if agg == "average" else sub["value"].sum()

        v_cy = period_value(start, end)
        v_py = period_value(py_start, py_end)
        pct = None
        if v_cy is not None and v_py and v_py != 0:
            pct = (v_cy - v_py) / v_py * 100
        rows.append((metric_name, fmt_value(v_cy, fmt), fmt_value(v_py, fmt), pct))
    return rows


def build_html(rows, period_label, mode):
    title = "Weekly Summary" if mode == "weekly" else "Monthly Summary"
    trs = []
    for name, cy, py, pct in rows:
        if pct is None:
            pct_html = f'<span style="color:{MUTED}">—</span>'
        else:
            color = POSITIVE if pct >= 0 else NEGATIVE
            arrow = "▲" if pct >= 0 else "▼"
            pct_html = f'<span style="color:{color};font-weight:600">{arrow} {abs(pct):.1f}%</span>'
        trs.append(
            f"<tr>"
            f'<td style="padding:8px 12px;border-bottom:1px solid #eee">{name}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:600">{cy}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;color:{MUTED}">{py}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right">{pct_html}</td>'
            f"</tr>"
        )
    return f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:640px;margin:0 auto">
      <h2 style="margin-bottom:4px">{title} — {period_label}</h2>
      <p style="color:{MUTED};margin-top:0">Priceline Pharmacy Pacific Fair · vs same period last year</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px">
        <tr style="background:#f4f4f6">
          <th style="padding:8px 12px;text-align:left">Metric</th>
          <th style="padding:8px 12px;text-align:right">This Year</th>
          <th style="padding:8px 12px;text-align:right">Last Year</th>
          <th style="padding:8px 12px;text-align:right">Change</th>
        </tr>
        {''.join(trs)}
      </table>
      <p style="color:{MUTED};font-size:12px">Generated automatically by your pharmacy dashboard.</p>
    </div>
    """


def send_email(html, subject):
    with open(RESEND_KEY_FILE) as f:
        api_key = f.read().strip()
    payload = json.dumps({
        "from": FROM_EMAIL,
        "to": [TO_EMAIL],
        "subject": subject,
        "html": html,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "pharmacy-dashboard/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Email sent ({resp.status}): {subject}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"Resend API error {e.code}: {body}")
        sys.exit(1)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "weekly"
    if mode not in ("weekly", "monthly"):
        print("Usage: python email_report.py [weekly|monthly]")
        sys.exit(1)

    start, end, period_label = get_period(mode)
    print(f"Building {mode} report for {start} to {end}...")

    client = data_module.connect_to_google_sheets()
    all_data = data_module.load_all_data(client)
    if not all_data:
        print("No data loaded — aborting.")
        sys.exit(1)

    rows = build_summary(all_data, start, end)
    html = build_html(rows, period_label, mode)
    title = "Weekly" if mode == "weekly" else "Monthly"
    send_email(html, f"Pharmacy {title} Summary — {period_label}")


if __name__ == "__main__":
    main()
