# Archived one-off scripts

These scripts were used **once** to backfill historical FY 22/23 front-shop data and to
debug that process. They are kept for reference only. **Do not run them again without
reading this first.**

| Script | What it did |
|--------|-------------|
| `inspect_2223.py` | Printed the layout of the historical `22/23` tab and the DETAILS tabs. |
| `migrate_2223.py` | ⚠️ Wrote FY 22/23 rows **into `FRONT SHOP DETAILS`** — this broke the yearly-tab formulas. Superseded. |
| `fix_backfill.py` | ⚠️ Cleaned up mis-aligned rows that `migrate_2223.py` appended. |
| `check_backfill.py` / `check_raw.py` | Read-only verification of what the dashboard/sheet saw. |
| `move_backfill.py` | ✅ The correct approach: removed the backfill from `FRONT SHOP DETAILS` and put it in the separate read-only `DASHBOARD HISTORY` tab. |

## The lesson (see the root README's "Hard rules")

Never write rows into `FRONT SHOP DETAILS` or `DISPENSARY DETAILS` — their layout feeds
fragile formulas in the yearly tabs, and appending rows silently corrupts them. Any
historical data the dashboard should read belongs in the **`DASHBOARD HISTORY`** tab, which
the dashboard merges in automatically (details rows always win for the same date).
