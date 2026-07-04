"""Print raw bottom rows of FRONT SHOP DETAILS as gspread sees them."""
import gspread
from google.oauth2.service_account import Credentials

import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]
creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
ss = client.open(config.SPREADSHEET_NAME)
ws = ss.worksheet(config.FRONT_SHOP_TAB)

values = ws.get_all_values()
print(f"Worksheet grid: {ws.row_count} rows x {ws.col_count} cols")
print(f"Rows returned by get_all_values: {len(values)}")
print("\nLast 8 rows:")
for i, row in enumerate(values[-8:], start=len(values) - 7):
    print(f"  Row {i}: {row[:6]}")

# Any rows mentioning 2022?
hits = [(i + 1, row[:3]) for i, row in enumerate(values) if "2022" in (row[0] if row else "")]
print(f"\nRows whose first cell contains '2022': {len(hits)}")
for r, cells in hits[:5]:
    print(f"  Row {r}: {cells}")
if len(hits) > 5:
    print(f"  ... and {len(hits) - 5} more (last: Row {hits[-1][0]}: {hits[-1][1]})")
