
import requests
from math import isclose

url = "http://127.0.0.1:8000/api/metrics"

response = requests.get(
    url,
    params={"month": "2026-01"},
    timeout=180,
)
response.raise_for_status()
data = response.json()

daily = data["daily"]

print("Days returned:", len(daily))
print("Matched hours:", data["matchedHours"])
print("Expected hours:", data["expectedHours"])
print("Coverage:", data["coveragePercent"], "%")

print("\nDaily bias/MAE checks:")

for day in daily:
    if day["mae"] is None or day["bias"] is None:
        print(day["date"], "NO DATA")
        continue

    if isclose(day["mae"], day["bias"], abs_tol=0.01):
        print(
            day["date"],
            "MAE equals bias:",
            round(day["mae"], 2),
        )

print("\nFirst day:", daily[0])
print("Last day:", daily[-1])
