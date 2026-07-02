"""
One-off helper: prints the layout of the 22/23 tab (and the DETAILS tabs)
so the historical backfill can be mapped correctly.

Run:  python inspect_2223.py
Then copy/paste the output back to Claude.
"""
import gspread
from google.oauth2.service_account import Credentials

import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]

creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
ss = client.open(config.SPREADSHEET_NAME)

print("=== All tabs in the spreadsheet ===")
for ws in ss.worksheets():
    print(f"  {ws.title!r}  ({ws.row_count} rows x {ws.col_count} cols)")

def show(tab_name, n_rows=4):
    print(f"\n=== {tab_name} ===")
    try:
        ws = ss.worksheet(tab_name)
    except Exception as exc:
        print(f"  Could not open: {exc}")
        return
    values = ws.get_all_values()
    if not values:
        print("  (empty)")
        return
    print(f"  Total rows with content: {len(values)}")
    for i, row in enumerate(values[:n_rows]):
        print(f"  Row {i + 1}: {row}")
    # Show first and last data dates if recognisable
    if len(values) > 1:
        print(f"  Last row: {values[-1]}")

show("22/23")
show(config.FRONT_SHOP_TAB, n_rows=2)
show(config.DISPENSARY_TAB, n_rows=2)
