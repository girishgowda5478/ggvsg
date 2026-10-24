
from collections import defaultdict

from app.data_service import load_january_data
from app.evaluation import parse_time

_, forecasts = load_january_data()

delivery_date = "2026-01-15"
cutoff = parse_time("2026-01-14T10:00:00Z")

snapshots = defaultdict(set)

for row in forecasts:
    published = parse_time(row["publishTime"])
    target = parse_time(row["startTime"])

    if published > cutoff:
        continue

    if target.date().isoformat() != delivery_date:
        continue

    snapshots[published].add(target.hour)

expected = set(range(24))

for published, hours in sorted(snapshots.items()):
    missing = sorted(expected - hours)

    print(f"\nPublication: {published.isoformat()}")
    print("Forecast hours:", len(hours))
    print("Missing hours:", missing)
