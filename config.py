"""
Configuration for Pharmacy POS Dashboard.
Update SPREADSHEET_NAME and CREDENTIALS_FILE for your environment.
"""
import os

# Google Sheets configuration
SPREADSHEET_NAME = "YOUR_SPREADSHEET_NAME_HERE"
CREDENTIALS_FILE = os.path.expanduser("~/.pharmacy-dashboard/credentials.json")

# Year tab names in the spreadsheet
SHEET_NAMES = {
    "25/26": "25/26",
    "24/25": "24/25",
    "23/24": "23/24",
    "22/23": "22/23",
    "21/22": "21/22",
}

# Financial year starts in July
FY_START_MONTH = 7

# Header row in each year tab (0-indexed: row 184 in sheet = index 183)
HEADER_ROW = 184
DATA_START_ROW = 185

# Cache duration in seconds
CACHE_TTL = 300  # 5 minutes

# Column indices (0-based) for each metric
COLUMN_MAP = {
    "daily_sales": 1,           # B
    "tax_sales": 2,             # C
    "non_tax_sales": 3,         # D
    "net_sales": 4,             # E
    "tax_coll": 5,              # F
    "front_back_pct": 6,        # G
    "item_value": 7,            # H
    "ave_sale": 8,              # I
    "items_per_sale": 9,        # J
    "sisterclub_vouchers": 10,  # K
    "club_sales": 11,           # L
    "saleschk": 12,             # M
    "tax_chk": 13,              # N
    "rounding": 14,             # O
    "under_over": 15,           # P
    "till": 16,                 # Q
    "cash_for_bank": 17,        # R
    "eftpos": 18,               # S
    "gift_card": 19,            # T
    "click_collect": 20,        # U
    "acnt_sale_paid": 21,       # V
    "overage_variance": 22,     # W
    "items": 23,                # X
    "cust_memb": 24,            # Y
    "count_non_mb": 25,         # Z
    "tot_cust": 26,             # AA
    "mem_no_pct": 27,           # AB
    "patient_cont_incl_s3": 28, # AC
    "govt_rec": 29,             # AD
    "pat_cont_less_s3": 30,     # AE
    "dly_sales_tax_govt": 31,   # AF
    "prior_yr_scripts": 32,     # AG
    "diff": 33,                 # AH
    "script_nos": 34,           # AI
    "cont_scpt": 35,            # AJ
    "total_script": 36,         # AK
    "safety_net": 37,           # AL
    "general": 38,              # AM
    "concession": 39,           # AN
    "entitlement": 40,          # AO
    "repat": 41,                # AP
    "private": 42,              # AQ
    "s3_record": 43,            # AR
    "gross_profit": 44,         # AS
    "gp_running_ttl": 45,       # AT
    "prior_yr_date": 46,        # AU
    "day": 47,                  # AV
    "sister_club_win_lose": 48, # AW
    "amex": 49,                 # AX
    "monthly_tot_priceline": 50,# AY
    "yearly_total": 51,         # AZ
    "landlord_net": 52,         # BA
    "landlord_reporting": 53,   # BB
    "total_plus_gov": 54,       # BC
}

# The 22 metrics available in the dashboard dropdown
METRICS = {
    "Daily Sales": {
        "key": "daily_sales",
        "col_index": COLUMN_MAP["daily_sales"],
        "format": "currency",
        "aggregation": "sum",
        "category": "front_shop",
    },
    "Net Sales": {
        "key": "net_sales",
        "col_index": COLUMN_MAP["net_sales"],
        "format": "currency",
        "aggregation": "sum",
        "category": "front_shop",
    },
    "Average Sale": {
        "key": "ave_sale",
        "col_index": COLUMN_MAP["ave_sale"],
        "format": "currency",
        "aggregation": "average",
        "category": "front_shop",
    },
    "Items Per Sale": {
        "key": "items_per_sale",
        "col_index": COLUMN_MAP["items_per_sale"],
        "format": "number_2dp",
        "aggregation": "average",
        "category": "front_shop",
    },
    "Sisterclub Sales": {
        "key": "club_sales",
        "col_index": COLUMN_MAP["club_sales"],
        "format": "currency",
        "aggregation": "sum",
        "category": "front_shop",
    },
    "Cash": {
        "key": "cash_for_bank",
        "col_index": COLUMN_MAP["cash_for_bank"],
        "format": "currency",
        "aggregation": "sum",
        "category": "front_shop",
    },
    "Click & Collect": {
        "key": "click_collect",
        "col_index": COLUMN_MAP["click_collect"],
        "format": "currency",
        "aggregation": "sum",
        "category": "front_shop",
    },
    "Patient Contribution Incl S3s": {
        "key": "patient_cont_incl_s3",
        "col_index": COLUMN_MAP["patient_cont_incl_s3"],
        "format": "currency",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Government Recovery": {
        "key": "govt_rec",
        "col_index": COLUMN_MAP["govt_rec"],
        "format": "currency",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Daily Sales - Tax + Gov Recovery": {
        "key": "dly_sales_tax_govt",
        "col_index": COLUMN_MAP["dly_sales_tax_govt"],
        "format": "currency",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Script Numbers": {
        "key": "script_nos",
        "col_index": COLUMN_MAP["script_nos"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Total Script": {
        "key": "total_script",
        "col_index": COLUMN_MAP["total_script"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Safety Net": {
        "key": "safety_net",
        "col_index": COLUMN_MAP["safety_net"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "General": {
        "key": "general",
        "col_index": COLUMN_MAP["general"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Concession": {
        "key": "concession",
        "col_index": COLUMN_MAP["concession"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Entitlement": {
        "key": "entitlement",
        "col_index": COLUMN_MAP["entitlement"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Repat": {
        "key": "repat",
        "col_index": COLUMN_MAP["repat"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Private": {
        "key": "private",
        "col_index": COLUMN_MAP["private"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "S3 Record": {
        "key": "s3_record",
        "col_index": COLUMN_MAP["s3_record"],
        "format": "number",
        "aggregation": "sum",
        "category": "dispensary",
    },
    "Landlord Net Sales - Tax - Gov": {
        "key": "landlord_net",
        "col_index": COLUMN_MAP["landlord_net"],
        "format": "currency",
        "aggregation": "sum",
        "category": "landlord",
    },
    "Landlord Reporting Figure": {
        "key": "landlord_reporting",
        "col_index": COLUMN_MAP["landlord_reporting"],
        "format": "currency",
        "aggregation": "sum",
        "category": "landlord",
    },
    "Total + Gov": {
        "key": "total_plus_gov",
        "col_index": COLUMN_MAP["total_plus_gov"],
        "format": "currency",
        "aggregation": "sum",
        "category": "landlord",
    },
}

# Dashboard colour scheme
COLORS = {
    "background": "#1a1a2e",
    "card": "#16213e",
    "card_border": "#0f3460",
    "accent": "#0f3460",
    "accent_light": "#533483",
    "text": "#ffffff",
    "text_muted": "#a0a0b8",
    "positive": "#00e676",
    "negative": "#ff5252",
    "line_cy": "#00b4d8",
    "line_py": "#f4a261",
    "line_2yr": "#e76f51",
    "table_header": "#0f3460",
    "table_row_alt": "#1a1a3e",
}

# Month labels for the financial year (Jul=1 through Jun=12)
FY_MONTH_LABELS = [
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
]
