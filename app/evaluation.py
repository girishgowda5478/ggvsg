
from collections import defaultdict
from datetime import datetime, timezone
from math import isfinite, sqrt


def parse_time(value: str) -> datetime:
    """Parse an ISO timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")

    return parsed.astimezone(timezone.utc)


def finite_generation(record: dict) -> float | None:
    """Return a finite generation value, or None for invalid data."""
    value = record.get("generation")

    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if isfinite(number) else None


def evaluate_forecasts(
    actual_records: list[dict],
    forecast_records: list[dict],
    delivery_date: str,
    cutoff: str,
) -> dict:
    """
    Compare hourly forecasts with hourly-average actual generation.

    Uses the latest forecast published at or before cutoff for each
    delivery hour. Actual records are deduplicated by startTime and
    an hour is included only when both distinct half-hours are present.

    Assumption: timestamps and values from both datasets have been
    validated to represent comparable delivery intervals and units.
    """
    date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
    cutoff_time = parse_time(cutoff)

    # Latest eligible forecast per delivery hour.
    selected = {}

    for record in forecast_records:
        delivery_time = parse_time(record["startTime"])
        publish_time = parse_time(record["publishTime"])

        if delivery_time.date() != date:
            continue

        if publish_time > cutoff_time:
            continue

        generation = finite_generation(record)

        if generation is None:
            continue

        hour = delivery_time.replace(
            minute=0, second=0, microsecond=0
        )
        existing = selected.get(hour)

        if (
            existing is None
            or publish_time > existing["publish_time"]
        ):
            selected[hour] = {
                "publish_time": publish_time,
                "generation": generation,
            }

    # Deduplicate actuals by exact half-hour start timestamp.
    actuals_by_hour = defaultdict(dict)

    for record in actual_records:
        delivery_time = parse_time(record["startTime"])

        if delivery_time.date() != date:
            continue

        generation = finite_generation(record)

        if generation is None:
            continue

        hour = delivery_time.replace(
            minute=0, second=0, microsecond=0
        )

        actuals_by_hour[hour][delivery_time] = generation

    comparisons = []

    for hour in sorted(selected):
        half_hours = actuals_by_hour.get(hour, {})

        # Require distinct starts at HH:00 and HH:30.
        expected_starts = {
            hour,
            hour.replace(minute=30),
        }

        if set(half_hours) != expected_starts:
            continue

        actual = sum(half_hours.values()) / 2
        forecast = selected[hour]["generation"]
        error = forecast - actual

        comparisons.append({
            "startTime": hour.isoformat(),
            "publishTime": selected[hour]["publish_time"].isoformat(),
            "forecastGeneration": forecast,
            "actualGeneration": actual,
            "error": error,
        })

    errors = [row["error"] for row in comparisons]
    count = len(errors)
    expected_hours = 24
    missing_hours = expected_hours - count

    return {
        "deliveryDate": delivery_date,
        "cutoff": cutoff_time.isoformat(),
        "expectedHours": expected_hours,
        "matchedHours": count,
        "missingHours": missing_hours,
        "coveragePercent": round(
            count / expected_hours * 100, 2
        ),
        "mae": (
            sum(abs(error) for error in errors) / count
            if count else None
        ),
        "rmse": (
            sqrt(sum(error * error for error in errors) / count)
            if count else None
        ),
        "bias": (
            sum(errors) / count
            if count else None
        ),
        "comparisons": comparisons,
    }
