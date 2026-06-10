"""
Data loading module for Pharmacy POS Dashboard.
Reads from FRONT SHOP DETAILS and DISPENSARY DETAILS tabs.
"""
import time
import re
from datetime import datetime, date

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

import config

_cache = {"data": None, "timestamp": 0}


def _cache_is_fresh():
    return _cache["data"] is not None and (time.time() - _cache["timestamp"]) < config.CACHE_TTL


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def connect_to_google_sheets(credentials_path=None):
    creds_path = credentials_path or config.CREDENTIALS_FILE
    credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(credentials)


_DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})")


def _parse_date(raw):
    if not raw:
        return None
    m = _DATE_RE.search(str(raw).strip())
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


def _to_float(val):
    if val is None or val == "":
        return None
    s = str(val).replace("$", "").replace(",", "").replace(" ", "").strip()
    if s in ("", "-", "#N/A", "#REF!", "#VALUE!", "#DIV/0!"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def get_fy_month(d):
    m = d.month - config.FY_START_MONTH + 1
    if m <= 0:
        m += 12
    return m


def get_fy_label(d):
    if d.month >= config.FY_START_MONTH:
        start_year = d.year
    else:
        start_year = d.year - 1
    end_year = start_year + 1
    return f"{start_year % 100:02d}/{end_year % 100:02d}"


def get_current_fy():
    return get_fy_label(date.today())


def get_prior_fy(fy_label, n=1):
    parts = fy_label.split("/")
    start = int(parts[0])
    end = int(parts[1])
    new_start = start - n
    new_end = end - n
    if new_start < 0:
        return None
    return f"{new_start:02d}/{new_end:02d}"


def _load_tab(client, spreadsheet_name, tab_name, col_map):
    spreadsheet = client.open(spreadsheet_name)
    worksheet = spreadsheet.worksheet(tab_name)
    all_values = worksheet.get_all_values()
    data_rows = all_values[1:]  # skip header row

    records = []
    for row in data_rows:
        if not row:
            continue
        parsed = _parse_date(row[0] if row else "")
        if parsed is None:
            continue

        record = {"date": parsed}
        for key, idx in col_map.items():
            if key == "date":
                continue
            record[key] = _to_float(row[idx] if idx < len(row) else None)
        records.append(record)

    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values("date", inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


def load_all_data(client, spreadsheet_name=None):
    ss_name = spreadsheet_name or config.SPREADSHEET_NAME

    try:
        fs_df = _load_tab(client, ss_name, config.FRONT_SHOP_TAB, config.FS_COLS)
    except Exception as exc:
        print(f"Warning: could not load Front Shop Details: {exc}")
        fs_df = pd.DataFrame()

    try:
        disp_df = _load_tab(client, ss_name, config.DISPENSARY_TAB, config.DISP_COLS)
    except Exception as exc:
        print(f"Warning: could not load Dispensary Details: {exc}")
        disp_df = pd.DataFrame()

    if fs_df.empty and disp_df.empty:
        return {}

    # Merge on date
    if not fs_df.empty and not disp_df.empty:
        combined = pd.merge(fs_df, disp_df, on="date", how="outer")
    elif not fs_df.empty:
        combined = fs_df
    else:
        combined = disp_df

    combined.sort_values("date", inplace=True)
    combined.reset_index(drop=True, inplace=True)

    # Calculated fields
    if "daily_sales" in combined.columns and "tot_cust" in combined.columns:
        combined["ave_sale"] = combined.apply(
            lambda r: r["daily_sales"] / r["tot_cust"] if r.get("tot_cust") and r["tot_cust"] > 0 else None,
            axis=1,
        )
    if "items" in combined.columns and "tot_cust" in combined.columns:
        combined["items_per_sale"] = combined.apply(
            lambda r: r["items"] / r["tot_cust"] if r.get("tot_cust") and r["tot_cust"] > 0 else None,
            axis=1,
        )
    if "daily_sales" in combined.columns and "tax_sales" in combined.columns and "govt_rec" in combined.columns:
        combined["dly_sales_tax_govt"] = combined.apply(
            lambda r: (r.get("daily_sales") or 0) - (r.get("tax_sales") or 0) + (r.get("govt_rec") or 0),
            axis=1,
        )
    if "daily_sales" in combined.columns and "govt_rec" in combined.columns:
        combined["total_plus_gov"] = combined.apply(
            lambda r: (r.get("daily_sales") or 0) + (r.get("govt_rec") or 0),
            axis=1,
        )

    # Add FY columns
    combined["fy_year"] = combined["date"].apply(get_fy_label)
    combined["fy_month"] = combined["date"].apply(get_fy_month)

    # Split into dict keyed by FY
    result = {}
    for fy, group in combined.groupby("fy_year"):
        result[fy] = group.reset_index(drop=True)

    return result


def get_metric_data(all_data, metric_key):
    frames = []
    for fy_label, df in all_data.items():
        if df.empty or metric_key not in df.columns:
            continue
        sub = df[["date", metric_key, "fy_year", "fy_month"]].copy()
        sub = sub.rename(columns={metric_key: "value"})
        sub["calendar_month"] = sub["date"].apply(lambda d: d.month)
        sub.dropna(subset=["value"], inplace=True)
        frames.append(sub)
    if not frames:
        return pd.DataFrame(columns=["date", "value", "fy_year", "fy_month", "calendar_month"])
    return pd.concat(frames, ignore_index=True)


def get_all_data(force_refresh=False):
    if not force_refresh and _cache_is_fresh():
        return _cache["data"]
    try:
        client = connect_to_google_sheets()
        data = load_all_data(client)
        _cache["data"] = data
        _cache["timestamp"] = time.time()
        return data
    except Exception as exc:
        print(f"Error loading data: {exc}")
        if _cache["data"] is not None:
            return _cache["data"]
        return None
