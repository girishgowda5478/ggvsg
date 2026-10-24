
from collections import Counter
from app.data_service import load_january_data
from app.evaluation import evaluate_forecasts

actuals, forecasts = load_january_data()

result = evaluate_forecasts(
    actuals,
    forecasts,
    "2026-01-15",
    "2026-01-14T10:00:00Z",
)

print("Selected cutoff:", result["cutoff"])
print("Matched hours:", result["matchedHours"])
print("Coverage:", result["coveragePercent"], "%")

publish_times = Counter(
    row["publishTime"] for row in result["comparisons"]
)
print("Selected forecast publication(s):", publish_times)

print("\nFirst three comparisons:")
for row in result["comparisons"][:3]:
    print(row)

print("\nActual timestamps for first delivery hour:")
for row in actuals:
    if row.get("startTime", "").startswith("2026-01-15T00:"):
        print(row["startTime"], row["generation"])
