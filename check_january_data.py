
from app.elexon import fetch_wind_actuals, fetch_wind_forecasts

# One-day smoke test before downloading the full month.
actuals = fetch_wind_actuals(
    "2026-01-01T00:00:00Z",
    "2026-01-02T00:00:00Z",
)

forecasts = fetch_wind_forecasts(
    "2025-12-31T00:00:00Z",
    "2026-01-02T00:00:00Z",
)

print("Actual wind records:", len(actuals))
print("Forecast records:", len(forecasts))

if actuals:
    print("First actual:", actuals[0])

if forecasts:
    print("First forecast:", forecasts[0])
