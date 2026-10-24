
from collections import defaultdict
from statistics import mean

from app.data_service import load_january_data
from app.evaluation import parse_time

actuals, forecasts = load_january_data()

delivery_date = "2026-01-15"
cutoff = parse_time("2026-01-14T10:00:00Z")

# Aggregate the two half-hourly actuals into hourly averages.
actual_by_hour = defaultdict(list)

for row in actuals:
    timestamp = parse_time(row["startTime"])

    if timestamp.date().isoformat() != delivery_date:
        continue

    hour = timestamp.replace(minute=0, second=0, microsecond=0)
    actual_by_hour[hour].append(float(row["generation"]))

hourly_actuals = {
    hour: mean(values)
    for hour, values in actual_by_hour.items()
    if len(values) == 2
}

# Evaluate each eligible publication snapshot separately.
by_publication = defaultdict(dict)

for row in forecasts:
    target = parse_time(row["startTime"])
    published = parse_time(row["publishTime"])

    if target.date().isoformat() != delivery_date:
        continue

    if published > cutoff:
        continue

    hour = target.replace(minute=0, second=0, microsecond=0)
    by_publication[published][hour] = float(row["generation"])

print("Complete actual hours:", len(hourly_actuals))
print("\nSnapshot comparison:")

for published, snapshot in sorted(by_publication.items()):
    errors = [
        forecast - hourly_actuals[hour]
        for hour, forecast in snapshot.items()
        if hour in hourly_actuals
    ]

    if not errors:
        continue

    print(
        published.isoformat(),
        "| matched:", len(errors),
        "| MAE:", round(mean(abs(e) for e in errors), 2),
        "| bias:", round(mean(errors), 2),
        "| negative errors:", sum(e < 0 for e in errors),
        "| positive errors:", sum(e > 0 for e in errors),
    )
