# Pharmacy POS Dashboard

A private analytics dashboard for **Priceline Pharmacy Pacific Fair**. It reads daily
point-of-sale data from a Google Sheet and presents it as an interactive, multi-year
dashboard (Python + [Dash](https://dash.plotly.com/) + Plotly).

The dashboard shows **turnover and operational metrics only** — no net-profit figures.

---

## What it does

- Reads two Google Sheet tabs — `FRONT SHOP DETAILS` and `DISPENSARY DETAILS` — plus an
  optional read-only `DASHBOARD HISTORY` tab (backfilled older days) and a `WAGES` tab.
- Presents ~20 metrics across three groups (Whole Shop / Front Shop / Dispensary),
  configured entirely in `config.py`.
- All comparisons use the **Australian financial year** (Jul–Jun) and are like-for-like:
  prior years are capped at the most recent uploaded date.
- Data is cached for 5 minutes and refreshes automatically; a **Refresh Now** button
  forces an immediate reload.

### Tabs
| Tab | Purpose |
|-----|---------|
| Overview | YTD cards for every metric vs the same point last year |
| Metric Detail | One metric: YTD/MTD cards + monthly chart & table vs up to 4 prior years |
| Month Detail | One month, days on the x-axis, year over year |
| FY Comparison | Any two financial years side by side + a year-by-year progression table (printable) |
| Trends | Rolling averages, script-type mix, scripts vs front-shop correlation |
| Day of Week | Average by weekday, selectable years |
| Monthly Compare | Months on the x-axis, grouped bars, selectable years |
| Wages % | Staff wages + super as a % of turnover, by FY month (from the `WAGES` tab) |
| Custom Range | Any date range vs the same dates in prior years |
| Monthly Report | Printable one-month summary |

---

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:8050>.

You need a Google service-account credentials file at
`~/.pharmacy-dashboard/credentials.json` (Windows: `C:\Users\<you>\.pharmacy-dashboard\`).
See `setup_guide.md` for the full first-time setup (Python install, Google Cloud project,
service account, sharing the sheet).

On Windows you can also double-click `run.bat`.

---

## Deployment (phone access)

The app runs unchanged locally, and can be hosted so it's reachable from a phone:

- **PythonAnywhere** (always-on, free): manual WSGI setup, `git pull` to update.
- **Render** (`render.yaml` included, free): auto-deploys on every push, sleeps when idle.

Both are protected by HTTP Basic Auth. Hosting is enabled by two environment variables
(never commit these):

| Variable | Purpose |
|----------|---------|
| `DASH_PASSWORD` | Enables the login prompt (username defaults to `jason`, override with `DASH_USER`). |
| `GOOGLE_CREDENTIALS_JSON` | Full contents of `credentials.json`, used instead of the file on hosts with no filesystem secret. |

When neither is set (i.e. local use), there is no password and the app reads
`credentials.json` from disk as before.

---

## Hard rules (do not break)

1. **Never commit** `credentials.json` or the Resend API key — `.gitignore` covers them.
2. **Never write to** the `FRONT SHOP DETAILS` or `DISPENSARY DETAILS` tabs. Their rows feed
   fragile formulas in the yearly tabs; appending rows there breaks them. The dashboard's
   service account is scoped **read-only** — keep it that way. Historical backfill lives in
   the separate `DASHBOARD HISTORY` tab instead.
3. **Turnover only** — no net-profit figures anywhere in the dashboard.

---

## Project layout

```
app.py            Dash app: layout, all tab builders, the main callback
config.py         Metrics, column maps, palettes, tab names, targets
data.py           Google Sheets loading, caching, FY helpers, timezone helpers
holidays.py       QLD public holidays (computed, no network)
email_report.py   Weekly/monthly email summaries via Resend (run manually or scheduled)
assets/           CSS + JS (theme, keyboard shortcuts)
render.yaml       Render.com deployment config
setup_guide.md    Step-by-step first-time setup
scripts/archive/  One-off historical-data migration scripts (see its README — do not reuse blindly)
```

---

## Notes

- Times use the `Australia/Brisbane` timezone (`data.today()` / `data.now()`) so hosted
  servers running in UTC still roll the day over at the right moment.
- Optional daily targets can be drawn on the Trends chart via `TARGETS` in `config.py`.
