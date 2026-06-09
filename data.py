"""
Data loading module for Pharmacy POS Dashboard.
Handles Google Sheets connection, data parsing, and caching.
"""
import time
import re
from datetime import datetime, date

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

import config

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache = {
    "data": None,
    "timestamp": 0,
}


def _cache_is_fresh() -> bool:
    return (
        _cache["data"] is not None
        and (time.time() - _cache["timestamp"]) < config.CACHE_TTL
    )


# ---------------------------------------------------------------------------
# Google Sheets connection
# ---------------------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def connect_to_google_sheets(credentials_path: str | None = None) -> gspread.Client:
    """Return an authorised gspread client."""
    creds_path = credentials_path or config.CREDENTIALS_FILE
    credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(credentials)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------
_DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")


def _parse_date(raw: str) -> date | None:
    """Extract a date from strings like '07/07/2025  Monday'."""
    if not raw:
        return None
    m = _DATE_RE.search(str(raw).strip())
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


def _to_float(val) -> float | None:
    """Convert a cell value to float, stripping $ and commas."""
    if val is None or val == "":
        return None
    s = str(val).replace("$", "").replace(",", "").replace(" ", "").strip()
    if s in ("", "-", "#N/A", "#REF!", "#VALUE!", "#DIV/0!"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Load a single year tab
# ---------------------------------------------------------------------------
def load_year_data(
    client: gspread.Client,
    spreadsheet_name: str,
    sheet_name: str,
) -> pd.DataFrame:
    """Read daily rows from one year tab, filtering out weekly summary rows."""
    spreadsheet = client.open(spreadsheet_name)
    worksheet = spreadsheet.worksheet(sheet_name)

    # Fetch all values from data start row onwards (row 185, 1-indexed)
    all_values = worksheet.get_all_values()
    data_rows = all_values[config.DATA_START_ROW - 1 :]  # 0-indexed slice

    records = []
    for row in data_rows:
        if not row:
            continue
        raw_date = row[0] if len(row) > 0 else ""
        parsed = _parse_date(raw_date)
        if parsed is None:
            # Weekly summary or blank row – skip
            continue

        record = {"date": parsed}
        for metric_name, meta in config.METRICS.items():
            idx = meta["col_index"]
            val = row[idx] if idx < len(row) else None
            record[meta["key"]] = _to_float(val)
        records.append(record)

    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values("date", inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


# ---------------------------------------------------------------------------
# Load all years
# ---------------------------------------------------------------------------
def load_all_years(
    client: gspread.Client,
    spreadsheet_name: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Return a dict of DataFrames keyed by financial year label."""
    ss_name = spreadsheet_name or config.SPREADSHEET_NAME
    result = {}
    for fy_label, tab_name in config.SHEET_NAMES.items():
        try:
            result[fy_label] = load_year_data(client, ss_name, tab_name)
        except Exception as exc:
            print(f"Warning: could not load tab '{tab_name}': {exc}")
            result[fy_label] = pd.DataFrame()
    return result


# ---------------------------------------------------------------------------
# Financial-year helpers
# ---------------------------------------------------------------------------
def get_current_fy() -> str:
    """Return the current financial year label, e.g. '25/26'."""
    today = date.today()
    if today.month >= config.FY_START_MONTH:
        start_year = today.year
    else:
        start_year = today.year - 1
    end_year = start_year + 1
    return f"{start_year % 100:02d}/{end_year % 100:02d}"


def get_prior_fy(fy_label: str, n: int = 1) -> str | None:
    """Return the FY label n years before the given one, or None."""
    parts = fy_label.split("/")
    start = int(parts[0])
    end = int(parts[1])
    new_start = start - n
    new_end = end - n
    if new_start < 0:
        return None
    label = f"{new_start:02d}/{new_end:02d}"
    return label if label in config.SHEET_NAMES else None


def get_fy_month(d: date) -> int:
    """Return 1-12 where 1=July, 12=June."""
    m = d.month - config.FY_START_MONTH + 1
    if m <= 0:
        m += 12
    return m


# ---------------------------------------------------------------------------
# Get metric data across years
# ---------------------------------------------------------------------------
def get_metric_data(
    all_data: dict[str, pd.DataFrame],
    metric_key: str,
) -> pd.DataFrame:
    """Combine metric values from all years into one DataFrame."""
    frames = []
    for fy_label, df in all_data.items():
        if df.empty or metric_key not in df.columns:
            continue
        sub = df[["date", metric_key]].copy()
        sub = sub.rename(columns={metric_key: "value"})
        sub["fy_year"] = fy_label
        sub["fy_month"] = sub["date"].apply(get_fy_month)
        sub["calendar_month"] = sub["date"].apply(lambda d: d.month)
        sub.dropna(subset=["value"], inplace=True)
        frames.append(sub)
    if not frames:
        return pd.DataFrame(columns=["date", "value", "fy_year", "fy_month", "calendar_month"])
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Cached data loader (called from app callbacks)
# ---------------------------------------------------------------------------
def get_all_data(force_refresh: bool = False) -> dict[str, pd.DataFrame] | None:
    """Return cached data, refreshing if stale. Returns None on error."""
    if not force_refresh and _cache_is_fresh():
        return _cache["data"]

    try:
        client = connect_to_google_sheets()
        data = load_all_years(client)
        _cache["data"] = data
        _cache["timestamp"] = time.time()
        return data
    except Exception as exc:
        print(f"Error loading data: {exc}")
        # Return stale cache if available
        if _cache["data"] is not None:
            return _cache["data"]
        return None
