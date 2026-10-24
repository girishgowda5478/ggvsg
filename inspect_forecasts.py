
import requests
from collections import Counter

URL = (
    "https://data.elexon.co.uk/bmrs/api/v1/"
    "datasets/WINDFOR/stream"
)

params = {
    "publishDateTimeFrom": "2026-01-14T00:00:00Z",
    "publishDateTimeTo": "2026-01-15T00:00:00Z",
    "format": "json",
}

response = requests.get(URL, params=params, timeout=60)
print("HTTP status:", response.status_code)
response.raise_for_status()

records = response.json()

if isinstance(records, dict):
    records = records.get("data", [])

print("Total forecast records:", len(records))

# Count records by publication timestamp.
snapshots = Counter(
    record["publishTime"] for record in records
)

print("\nPublication snapshots:")
for publish_time, count in sorted(snapshots.items()):
    print(f"{publish_time}: {count} records")

# Inspect forecasts targeting the selected delivery date.
target = [
    record for record in records
    if record.get("startTime", "").startswith("2026-01-15")
]

print("\nForecasts targeting 15 January:", len(target))

for record in target[:10]:
    print(record)
