
import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
TIMEOUT = 60


def fetch_dataset(
    dataset: str,
    publish_from: str,
    publish_to: str,
) -> list[dict]:
    """Fetch records published within a specified UTC window."""

    if dataset not in {"FUELHH", "WINDFOR"}:
        raise ValueError("Unsupported Elexon dataset")

    url = f"{BASE_URL}/{dataset}/stream"

    response = requests.get(
        url,
        params={
            "publishDateTimeFrom": publish_from,
            "publishDateTimeTo": publish_to,
            "format": "json",
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    records = response.json()

    if isinstance(records, dict):
        records = records.get("data", [])

    if not isinstance(records, list):
        raise ValueError("Unexpected Elexon API response format")

    return records


def fetch_wind_actuals(
    publish_from: str,
    publish_to: str,
) -> list[dict]:
    """Retrieve actual wind generation records."""

    records = fetch_dataset(
        "FUELHH", publish_from, publish_to
    )

    return [
        record
        for record in records
        if record.get("fuelType") == "WIND"
        and record.get("generation") is not None
    ]


def fetch_wind_forecasts(
    publish_from: str,
    publish_to: str,
) -> list[dict]:
    """Retrieve wind generation forecast records."""

    records = fetch_dataset(
        "WINDFOR", publish_from, publish_to
    )

    return [
        record
        for record in records
        if record.get("generation") is not None
        and record.get("startTime")
        and record.get("publishTime")
    ]
