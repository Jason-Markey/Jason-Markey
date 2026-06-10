"""
Configuration for Pharmacy POS Dashboard.
"""
import os

SPREADSHEET_NAME = "Journal - Priceline Pharmacy Pacific Fair (Jason)"
CREDENTIALS_FILE = os.path.join(os.path.expanduser("~"), ".pharmacy-dashboard", "credentials.json")

FY_START_MONTH = 7
CACHE_TTL = 300  # 5 minutes

# Source tabs
FRONT_SHOP_TAB = "FRONT SHOP DETAILS"
DISPENSARY_TAB = "DISPENSARY DETAILS"

# Front Shop Details columns (0-based, row 1 = headers, row 2+ = data)
FS_COLS = {
    "date": 0,            # A
    "daily_sales": 1,     # B
    "tax_sales": 2,       # C
    "non_tax_sales": 3,   # D
    "net_sales": 4,       # E
    "tax_coll": 5,        # F
    "sisterclub_vouchers": 6,  # G
    "club_sales": 7,      # H
    "rounding": 8,        # I
    "till": 9,            # J
    "cash_for_bank": 10,  # K
    "eftpos": 11,         # L
    "gift_card": 12,      # M
    "click_collect": 13,  # N
    "acnt_sale_paid": 14, # O
    "items": 15,          # P
    "cust_memb": 16,      # Q
    "count_non_mb": 17,   # R
    "tot_cust": 18,       # S
    "amex": 19,           # T
}

# Dispensary Details columns (0-based, row 1 = headers, row 2+ = data)
DISP_COLS = {
    "date": 0,                  # A
    "patient_cont_incl_s3": 1,  # B
    "govt_rec": 2,              # C
    "script_nos": 3,            # D
    "total_script": 4,          # E
    "safety_net": 5,            # F
    "general": 6,               # G
    "concession": 7,            # H
    "entitlement": 8,           # I
    "repat": 9,                 # J
    "private_disp": 10,         # K
    "s3_record": 11,            # L
    "gross_profit": 12,         # M
}

# Dashboard metrics — source tells us which tab, calculated means derived.
# "group" controls how metrics are grouped in the dropdown and Overview page.
METRICS = {
    # ── Whole Shop ──────────────────────────────────────────────────────
    "Daily Sales": {
        "key": "daily_sales",
        "source": "front_shop",
        "format": "currency",
        "aggregation": "sum",
        "group": "Whole Shop",
    },
    "Daily Sales - Tax + Gov Recovery": {
        "key": "dly_sales_tax_govt",
        "source": "calculated",
        "format": "currency",
        "aggregation": "sum",
        "group": "Whole Shop",
    },
    "Total + Gov": {
        "key": "total_plus_gov",
        "source": "calculated",
        "format": "currency",
        "aggregation": "sum",
        "group": "Whole Shop",
    },
    "Average Sale": {
        "key": "ave_sale",
        "source": "calculated",
        "format": "currency",
        "aggregation": "average",
        "group": "Whole Shop",
    },
    "Items Per Sale": {
        "key": "items_per_sale",
        "source": "calculated",
        "format": "number_2dp",
        "aggregation": "average",
        "group": "Whole Shop",
    },
    # ── Front Shop ──────────────────────────────────────────────────────
    "Front Shop Sales": {
        "key": "tax_sales",
        "source": "front_shop",
        "format": "currency",
        "aggregation": "sum",
        "group": "Front Shop",
    },
    "Sisterclub Sales": {
        "key": "club_sales",
        "source": "front_shop",
        "format": "currency",
        "aggregation": "sum",
        "group": "Front Shop",
    },
    "Click & Collect": {
        "key": "click_collect",
        "source": "front_shop",
        "format": "currency",
        "aggregation": "sum",
        "group": "Front Shop",
    },
    # ── Dispensary ──────────────────────────────────────────────────────
    "Dispensary Sales": {
        "key": "non_tax_sales",
        "source": "front_shop",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Dispensary Gross Profit": {
        "key": "gross_profit",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Script Numbers": {
        "key": "script_nos",
        "source": "dispensary",
        "format": "number",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Total Script": {
        "key": "total_script",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Patient Contribution Incl S3s": {
        "key": "patient_cont_incl_s3",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Government Recovery": {
        "key": "govt_rec",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Safety Net": {
        "key": "safety_net",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "General": {
        "key": "general",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Concession": {
        "key": "concession",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Entitlement": {
        "key": "entitlement",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Repat": {
        "key": "repat",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "Private": {
        "key": "private_disp",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
    "S3 Record": {
        "key": "s3_record",
        "source": "dispensary",
        "format": "currency",
        "aggregation": "sum",
        "group": "Dispensary",
    },
}

METRIC_GROUPS = ["Whole Shop", "Front Shop", "Dispensary"]

PALETTES = {
    "dark": {
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
    },
    "light": {
        "background": "#f2f3f7",
        "card": "#ffffff",
        "card_border": "#d8dce6",
        "accent": "#0f3460",
        "accent_light": "#533483",
        "text": "#1a1a2e",
        "text_muted": "#5a5f73",
        "positive": "#1a7d3c",
        "negative": "#b00020",
        "line_cy": "#0077b6",
        "line_py": "#e08a3c",
        "line_2yr": "#d04a2a",
        "table_header": "#e8eaf2",
        "table_row_alt": "#f4f5fa",
    },
}

COLORS = PALETTES["dark"]

FY_MONTH_LABELS = [
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
]
