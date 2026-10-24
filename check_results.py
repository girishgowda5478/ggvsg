
import requests

url = "http://127.0.0.1:8000/api/daily"

response = requests.get(
    url,
    params={"date": "2026-01-15"},
    timeout=120,
)
response.raise_for_status()
result = response.json()

rows = result.get("comparisons", [])
errors = [row["error"] for row in rows]

print("Delivery date:", result.get("deliveryDate"))
print("Cutoff:", result.get("cutoff"))
print("Matched hours:", result.get("matchedHours"))
print("MAE:", result.get("mae"))
print("RMSE:", result.get("rmse"))
print("Bias:", result.get("bias"))

print("Negative errors:", sum(e < 0 for e in errors))
print("Positive errors:", sum(e > 0 for e in errors))
print("Zero errors:", sum(e == 0 for e in errors))

if rows:
    print("\nFirst comparison:")
    print(rows[0])

    print("\nLast comparison:")
    print(rows[-1])

    print(
        "\nPublication timestamps within cutoff:",
        all(
            row["publishTime"] <= result["cutoff"]
            for row in rows
        ),
    )
