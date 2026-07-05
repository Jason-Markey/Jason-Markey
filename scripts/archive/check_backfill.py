"""Quick check: what FY 22/23 dates does the dashboard now see in FRONT SHOP DETAILS?"""
from datetime import date

import data as data_module

client = data_module.connect_to_google_sheets()
all_data = data_module.load_all_data(client)

df = data_module.get_metric_data(all_data, "daily_sales")
fy = df[df["fy_year"] == "22/23"]
print(f"FY 22/23 daily_sales rows: {len(fy)}")
if not fy.empty:
    print(f"Earliest: {fy['date'].min()}  Latest: {fy['date'].max()}")
    by_month = fy.groupby("fy_month")["value"].count()
    print("Days per FY month (1=Jul ... 12=Jun):")
    print(by_month.to_string())
