"""
One-off backfill: copy missing FY 22/23 daily rows from the historical
'22/23' tab into FRONT SHOP DETAILS and DISPENSARY DETAILS.

- Matches columns by HEADER NAME, never by position.
- Only adds dates that are missing from the DETAILS tabs.
- Never overwrites or edits existing rows (new rows are appended;
  the dashboard sorts by date, so order in the sheet doesn't matter).

Usage:
    python migrate_2223.py           # dry run — shows what WOULD be added
    python migrate_2223.py --apply   # actually writes the rows

Requires the service account to have EDITOR access to the spreadsheet
(you can set it back to Viewer afterwards).
"""
import re
import sys
from datetime import date, datetime

import gspread
from google.oauth2.service_account import Credentials

import config

SOURCE_TAB = "22/23"
FY_START = date(2022, 7, 1)
FY_END = date(2023, 6, 30)

# DETAILS-tab column key -> header text in the 22/23 tab (matched after strip())
FS_SOURCE_HEADERS = {
    "date": "DATE",
    "daily_sales": "Daily Sales",
    "tax_sales": "Tax Sales",
    "non_tax_sales": "Non Tax Sales",
    "net_sales": "Net Sales",
    "tax_coll": "Tax Coll",
    "sisterclub_vouchers": "Sister ClubVouchers",
    "club_sales": "Club sales",
    "rounding": "rounding",
    "till": "Till",
    "cash_for_bank": "Cash for bank",
    "eftpos": "Eftpos",
    "gift_card": "Gift card",
    "click_collect": "Click & Collect",
    "acnt_sale_paid": "Acnt Sale or  Paid",
    "items": "Items",
    "cust_memb": "Cust Memb",
    "count_non_mb": "Count Non-Mb",
    "tot_cust": "Tot Cust",
    "amex": "AMEX",
}
DISP_SOURCE_HEADERS = {
    "date": "DATE",
    "patient_cont_incl_s3": "Patient Cont Incl S3's",
    "govt_rec": "Govt Rec",
    "script_nos": "Script Nos",
    "total_script": "Total Script",
    "safety_net": "Safety Net",
    "general": "General",
    "concession": "Concess",
    "entitlement": "Entitle",
    "repat": "Repat",
    "private_disp": "Private",
    "s3_record": "S3 Record",
    "gross_profit": "Gross Profit",
}

_DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})")


def parse_date(raw):
    if not raw:
        return None
    m = _DATE_RE.search(str(raw))
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


def header_index_map(header_row, wanted):
    """Map our keys -> column index in the source tab, matching stripped header text."""
    stripped = [h.strip() for h in header_row]
    result = {}
    missing = []
    for key, header in wanted.items():
        target = header.strip()
        if target in stripped:
            result[key] = stripped.index(target)
        else:
            missing.append(header)
    return result, missing


def existing_dates(ws):
    dates = set()
    for row in ws.get_all_values()[1:]:
        d = parse_date(row[0] if row else "")
        if d:
            dates.add(d)
    return dates


def build_rows(source_rows, idx_map, col_map, add_dates):
    """Return list of (date, row_list) sized to the DETAILS tab layout."""
    width = max(col_map.values()) + 1
    out = []
    for row in source_rows:
        d = parse_date(row[idx_map["date"]] if idx_map["date"] < len(row) else "")
        if d is None or d not in add_dates:
            continue
        new_row = [""] * width
        new_row[col_map["date"]] = d.strftime("%d/%m/%Y")
        for key, dest_idx in col_map.items():
            if key == "date" or key not in idx_map:
                continue
            src_idx = idx_map[key]
            val = row[src_idx].strip() if src_idx < len(row) else ""
            new_row[dest_idx] = val
        out.append((d, new_row))
    out.sort(key=lambda t: t[0])
    return out


def main():
    apply_changes = "--apply" in sys.argv

    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive.readonly"]
    creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    ss = client.open(config.SPREADSHEET_NAME)

    src = ss.worksheet(SOURCE_TAB)
    src_values = src.get_all_values()
    header_row = src_values[1]  # row 2 holds the headers
    data_rows = src_values[2:]

    # Source dates within FY 22/23
    src_dates = set()
    for row in data_rows:
        d = parse_date(row[0] if row else "")
        if d and FY_START <= d <= FY_END:
            src_dates.add(d)
    print(f"'{SOURCE_TAB}' tab: {len(src_dates)} dated rows within FY 22/23 "
          f"({min(src_dates)} to {max(src_dates)})" if src_dates else "No FY 22/23 rows found!")

    for tab_name, source_headers, col_map in [
        (config.FRONT_SHOP_TAB, FS_SOURCE_HEADERS, config.FS_COLS),
        (config.DISPENSARY_TAB, DISP_SOURCE_HEADERS, config.DISP_COLS),
    ]:
        print(f"\n=== {tab_name} ===")
        idx_map, missing = header_index_map(header_row, source_headers)
        if missing:
            print(f"  WARNING — headers not found in '{SOURCE_TAB}' (these columns will be left blank): {missing}")

        ws = ss.worksheet(tab_name)
        have = existing_dates(ws)
        add_dates = {d for d in src_dates if d not in have}
        print(f"  Existing dated rows: {len(have)}; missing FY 22/23 dates to add: {len(add_dates)}")
        if not add_dates:
            print("  Nothing to do.")
            continue

        rows = build_rows(data_rows, idx_map, col_map, add_dates)
        print(f"  Date range to add: {rows[0][0]} to {rows[-1][0]}")
        print(f"  First row preview: {rows[0][1]}")
        print(f"  Last row preview:  {rows[-1][1]}")

        if apply_changes:
            ws.append_rows([r for _, r in rows], value_input_option="USER_ENTERED")
            print(f"  ✔ Added {len(rows)} rows to {tab_name}")
        else:
            print(f"  DRY RUN — would add {len(rows)} rows. Re-run with --apply to write them.")

    if not apply_changes:
        print("\nDry run complete. Nothing was changed.")
    else:
        print("\nDone. Open the dashboard and press 'Refresh Now' to see the backfilled data.")


if __name__ == "__main__":
    main()
