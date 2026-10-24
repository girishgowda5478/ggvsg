
from app.data_service import load_january_data

actuals, forecasts = load_january_data()

target_date = "2026-01-15"

print("\nACTUAL WIND RECORDS")
actual_samples = [
    row for row in actuals
    if row.get("startTime", "").startswith(target_date)
]

for row in actual_samples[:6]:
    print({
        key: row.get(key)
        for key in (
            "startTime",
            "settlementDate",
            "settlementPeriod",
            "fuelType",
            "generation",
        )
    })

print("\nFORECAST RECORDS")
forecast_samples = [
    row for row in forecasts
    if row.get("startTime", "").startswith(target_date)
]

for row in forecast_samples[:12]:
    print({
        key: row.get(key)
        for key in (
            "startTime",
            "publishTime",
            "settlementDate",
            "settlementPeriod",
            "generation",
        )
    })
