"""
Move the FY 22/23 backfill OUT of FRONT SHOP DETAILS into a dedicated
'DASHBOARD HISTORY' tab so existing sheet formulas are unaffected.

  1. Deletes the backfilled rows (the contiguous block below the last
     genuine 2026 row — every row is verified to be a 2022 date first).
  2. Creates a 'DASHBOARD HISTORY' tab (if missing) with the same column
     layout as FRONT SHOP DETAILS and writes the 163 days there.

The dashboard reads DASHBOARD HISTORY automatically (see data.py).

Usage:
    python move_backfill.py           # dry run
    python move_backfill.py --apply   # do it
"""
import sys
from datetime import date

import gspread
from google.oauth2.service_account import Credentials

import config
from migrate_2223 import (SOURCE_TAB, FY_START, FY_END, FS_SOURCE_HEADERS,
                          parse_date, header_index_map, build_rows)

HISTORY_TAB = "DASHBOARD HISTORY"

apply_changes = "--apply" in sys.argv

scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.readonly"]
creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
ss = client.open(config.SPREADSHEET_NAME)
ws = ss.worksheet(config.FRONT_SHOP_TAB)

values = ws.get_all_values()

# ── 1. Find the backfilled block: rows whose date is BEFORE the tab's
#      original first date (10/12/2022) — they can only be ours.
ORIGINAL_FIRST = date(2022, 12, 10)
block = []  # 1-based row indices
for i, row in enumerate(values, start=1):
    d = parse_date(row[0] if row else "")
    if d and d < ORIGINAL_FIRST:
        block.append(i)

print(f"Backfilled rows found in {config.FRONT_SHOP_TAB}: {len(block)}")
if block:
    print(f"  Row range: {min(block)}–{max(block)}")
    contiguous = (max(block) - min(block) + 1) == len(block)
    print(f"  Contiguous block: {contiguous}")
    if not contiguous:
        print("SAFETY STOP: rows are not contiguous — will not delete. Tell Claude.")
        sys.exit(1)
    if min(block) < 1000:
        print("SAFETY STOP: block starts suspiciously high in the sheet. Tell Claude.")
        sys.exit(1)

# ── 2. Rebuild the history rows from the 22/23 tab
src = ss.worksheet(SOURCE_TAB)
src_values = src.get_all_values()
idx_map, missing = header_index_map(src_values[1], FS_SOURCE_HEADERS)
if missing:
    print(f"WARNING — missing headers: {missing}")

# Dates the DETAILS tab will still have after we remove the backfill block
keep_dates = set()
for i, row in enumerate(values, start=1):
    if i in set(block):
        continue
    d = parse_date(row[0] if row else "")
    if d:
        keep_dates.add(d)

src_dates = set()
for row in src_values[2:]:
    d = parse_date(row[0] if row else "")
    if d and FY_START <= d <= FY_END:
        src_dates.add(d)
history_dates = {d for d in src_dates if d not in keep_dates}
rows = build_rows(src_values[2:], idx_map, config.FS_COLS, history_dates)

header = [""] * (max(config.FS_COLS.values()) + 1)
for key, idx in config.FS_COLS.items():
    header[idx] = key
print(f"\nRows to write to '{HISTORY_TAB}': {len(rows)}")
if rows:
    print(f"  Range: {rows[0][0]} to {rows[-1][0]}")

if not apply_changes:
    print("\nDRY RUN — nothing changed. Re-run with --apply.")
    sys.exit(0)

# ── 3. Apply: delete block from DETAILS
if block:
    ws.delete_rows(min(block), max(block))
    print(f"✔ Deleted rows {min(block)}–{max(block)} from {config.FRONT_SHOP_TAB}")

# ── 4. Create/replace the history tab and write rows
try:
    hist = ss.worksheet(HISTORY_TAB)
    hist.clear()
    print(f"✔ Cleared existing '{HISTORY_TAB}' tab")
except gspread.exceptions.WorksheetNotFound:
    hist = ss.add_worksheet(title=HISTORY_TAB, rows=len(rows) + 10,
                            cols=len(header))
    print(f"✔ Created '{HISTORY_TAB}' tab")

hist.update(
    values=[header] + [r for _, r in rows],
    range_name="A1",
    value_input_option="USER_ENTERED",
)
print(f"✔ Wrote {len(rows)} rows to '{HISTORY_TAB}'")
print("\nDone. Pull the latest dashboard code, restart it, and Refresh Now.")
