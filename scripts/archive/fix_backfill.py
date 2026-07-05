"""
Fix the botched 22/23 backfill in FRONT SHOP DETAILS.

The append API shifted the new rows into the wrong columns. This script:
  1. Finds the last genuine data row (last row with a valid date in column A).
  2. Deletes every row below it (the mis-aligned appended rows).
  3. Re-writes the missing FY 22/23 rows into an explicit A:T range,
     which cannot shift.

Usage:
    python fix_backfill.py           # dry run — analysis only
    python fix_backfill.py --apply   # delete junk rows and write clean rows
"""
import sys
from datetime import date

import gspread
from google.oauth2.service_account import Credentials

import config
from migrate_2223 import (SOURCE_TAB, FY_START, FY_END, FS_SOURCE_HEADERS,
                          parse_date, header_index_map, build_rows)

scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.readonly"]
creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
ss = client.open(config.SPREADSHEET_NAME)
ws = ss.worksheet(config.FRONT_SHOP_TAB)

apply_changes = "--apply" in sys.argv

values = ws.get_all_values()
total = len(values)

# Last genuine data row = last row with a valid date in column A (1-based index)
last_dated = 0
dated = set()
for i, row in enumerate(values, start=1):
    d = parse_date(row[0] if row else "")
    if d:
        last_dated = i
        dated.add(d)

junk_start = last_dated + 1
junk_rows = values[last_dated:] if total > last_dated else []
junk_nonempty = sum(1 for r in junk_rows if any(c.strip() for c in r))

print(f"Rows in sheet content: {total}")
print(f"Last genuine dated row: {last_dated} ({values[last_dated - 1][0]!r})")
print(f"Rows below it: {len(junk_rows)} ({junk_nonempty} contain stray content)")

if last_dated < 1000:
    print("SAFETY STOP: last dated row looks too small — aborting.")
    sys.exit(1)

# Rebuild the missing FY 22/23 rows from the source tab
src = ss.worksheet(SOURCE_TAB)
src_values = src.get_all_values()
idx_map, missing = header_index_map(src_values[1], FS_SOURCE_HEADERS)
if missing:
    print(f"WARNING — missing headers: {missing}")

src_dates = set()
for row in src_values[2:]:
    d = parse_date(row[0] if row else "")
    if d and FY_START <= d <= FY_END:
        src_dates.add(d)
add_dates = {d for d in src_dates if d not in dated}
rows = build_rows(src_values[2:], idx_map, config.FS_COLS, add_dates)
print(f"\nMissing FY 22/23 dates to write: {len(rows)}")
if rows:
    print(f"  Range: {rows[0][0]} to {rows[-1][0]}")
    print(f"  First row: {rows[0][1]}")
    print(f"  Last row:  {rows[-1][1]}")

if not apply_changes:
    print("\nDRY RUN — nothing changed. Re-run with --apply to fix.")
    sys.exit(0)

# 1) Delete the junk rows below the real data
if total > last_dated:
    ws.delete_rows(junk_start, total)
    print(f"✔ Deleted rows {junk_start}–{total}")

# 2) Write the clean rows into an explicit range starting right below the data
if rows:
    start_row = last_dated + 1
    end_row = start_row + len(rows) - 1
    ws.update(
        values=[r for _, r in rows],
        range_name=f"A{start_row}:T{end_row}",
        value_input_option="USER_ENTERED",
    )
    print(f"✔ Wrote {len(rows)} rows into A{start_row}:T{end_row}")

print("\nDone. Run 'python check_backfill.py' to verify, then Refresh Now in the dashboard.")
