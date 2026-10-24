
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

from app.elexon import fetch_wind_actuals, fetch_wind_forecasts


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@lru_cache(maxsize=4)
def load_january_data():
    """Load January 2026 actuals and forecast publication history."""

    actuals = []
    forecasts = []

    # Actuals: include all publications covering January delivery.
    actuals.extend(
        fetch_wind_actuals(
            "2026-01-01T00:00:00Z",
            "2026-02-01T00:00:00Z",
        )
    )

    # Forecast history: include the preceding days so the first
    # January delivery dates have eligible historical forecasts.
    start = datetime(2025, 12, 30, tzinfo=timezone.utc)
    end = datetime(2026, 1, 31, tzinfo=timezone.utc)

    current = start
    while current < end:
        next_day = min(current + timedelta(days=1), end)

        forecasts.extend(
            fetch_wind_forecasts(
                iso_utc(current),
                iso_utc(next_day),
            )
        )

        current = next_day

    # Keep actuals whose delivery intervals fall in January.
    actuals = [
        row for row in actuals
        if row["startTime"].startswith("2026-01-")
    ]

    return actuals, forecasts
