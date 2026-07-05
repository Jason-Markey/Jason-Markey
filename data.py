"""
Data loading module for Pharmacy POS Dashboard.
Reads from FRONT SHOP DETAILS and DISPENSARY DETAILS tabs.
"""
import os
import json
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
    # Cloud hosting: credentials supplied via environment variable instead of a file
    env_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if env_json and not credentials_path:
        info = json.loads(env_json)
        credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
        return gspread.authorize(credentials)
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

    # Optional history tab with backfilled old days (same layout as Front Shop).
    # Details rows always take precedence over history rows for the same date.
    try:
        hist_df = _load_tab(client, ss_name, config.HISTORY_TAB, config.FS_COLS)
        if not hist_df.empty:
            if not fs_df.empty:
                hist_df = hist_df[~hist_df["date"].isin(set(fs_df["date"]))]
                fs_df = pd.concat([hist_df, fs_df], ignore_index=True)
                fs_df.sort_values("date", inplace=True)
                fs_df.reset_index(drop=True, inplace=True)
            else:
                fs_df = hist_df
    except Exception:
        pass  # tab may not exist — that's fine

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
    if "cust_memb" in combined.columns and "tot_cust" in combined.columns:
        combined["memb_rate"] = combined.apply(
            lambda r: r["cust_memb"] / r["tot_cust"] * 100 if r.get("tot_cust") and r["tot_cust"] > 0 else None,
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


_wages_cache = {"data": None, "timestamp": 0}


def get_wages_data(force_refresh=False):
    """Monthly staff cost (wages + super, owner excluded) from the WAGES tab.

    Returns a DataFrame with columns: year, month, staff_cost.
    Empty DataFrame if the tab doesn't exist or can't be read.
    """
    if (not force_refresh and _wages_cache["data"] is not None
            and (time.time() - _wages_cache["timestamp"]) < config.CACHE_TTL):
        return _wages_cache["data"]

    empty = pd.DataFrame(columns=["year", "month", "staff_cost"])
    try:
        client = connect_to_google_sheets()
        ws = client.open(config.SPREADSHEET_NAME).worksheet(config.WAGES_TAB)
        values = ws.get_all_values()
    except Exception as exc:
        print(f"Warning: could not load {config.WAGES_TAB} tab: {exc}")
        return _wages_cache["data"] if _wages_cache["data"] is not None else empty

    if not values:
        return empty
    header = [h.strip().lower() for h in values[0]]

    def _col(name):
        name = name.lower()
        for i, h in enumerate(header):
            if h == name:
                return i
        return None

    i_month = _col("Month")
    i_wages = _col("Staff Wages ex Jason")
    i_super = _col("Staff Super ex Jason")
    if i_month is None or i_wages is None:
        print(f"Warning: {config.WAGES_TAB} tab is missing expected columns")
        return empty

    records = []
    for row in values[1:]:
        if i_month >= len(row):
            continue
        m = re.match(r"(\d{4})-(\d{1,2})", str(row[i_month]).strip())
        if not m:
            continue
        wages = _to_float(row[i_wages] if i_wages < len(row) else None) or 0.0
        sup = 0.0
        if i_super is not None and i_super < len(row):
            sup = _to_float(row[i_super]) or 0.0
        records.append({"year": int(m.group(1)), "month": int(m.group(2)),
                        "staff_cost": wages + sup})

    df = pd.DataFrame(records) if records else empty
    _wages_cache["data"] = df
    _wages_cache["timestamp"] = time.time()
    return df


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
