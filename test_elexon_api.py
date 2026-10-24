
import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"

# Query the publication window, not just the delivery window.
WINDOWS = {
    "FUELHH": (
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
    ),
    "WINDFOR": (
        "2025-12-31T00:00:00Z",
        "2026-01-02T00:00:00Z",
    ),
}

for dataset, (start, end) in WINDOWS.items():
    print(f"\n--- {dataset} ---")

    try:
        response = requests.get(
            f"{BASE_URL}/{dataset}/stream",
            params={
                "publishDateTimeFrom": start,
                "publishDateTimeTo": end,
                "format": "json",
            },
            timeout=60,
        )

        print("Request URL:", response.url)
        print("HTTP status:", response.status_code)
        response.raise_for_status()

        records = response.json()

        if isinstance(records, dict):
            records = records.get("data", [])

        print("Total records:", len(records))

        if dataset == "FUELHH":
            records = [
                r for r in records
                if r.get("fuelType") == "WIND"
            ]
            print("Wind records:", len(records))

        for record in records[:3]:
            print(record)

        if records:
            print(
                "Publish time range:",
                min(r["publishTime"] for r in records),
                "to",
                max(r["publishTime"] for r in records),
            )

    except (requests.RequestException, ValueError, KeyError) as exc:
        print("Request failed:", exc)
