
from collections import Counter
from app.elexon import fetch_wind_actuals

records = fetch_wind_actuals(
    "2026-01-01T00:00:00Z",
    "2026-02-01T00:00:00Z",
)

print("Total returned actual records:", len(records))

by_delivery_date = Counter(
    row["startTime"][:10]
    for row in records
    if row.get("startTime")
)

print("\nRecords by delivery date:")
for day in sorted(by_delivery_date):
    print(day, by_delivery_date[day])

print("\nFirst 5 records:")
for row in records[:5]:
    print(row)

print("\nLast 5 records:")
for row in records[-5:]:
    print(row)
