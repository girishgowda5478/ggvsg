
from app.evaluation import evaluate_forecasts


def test_selects_latest_forecast_before_cutoff():
    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T07:30:00Z",
            "generation": 100,
        },
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T09:30:00Z",
            "generation": 120,
        },
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 999,
        },
    ]

    actuals = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "generation": 110,
        },
        {
            "startTime": "2026-01-15T00:30:00Z",
            "generation": 130,
        },
    ]

    result = evaluate_forecasts(
        actual_records=actuals,
        forecast_records=forecasts,
        delivery_date="2026-01-15",
        cutoff="2026-01-14T10:00:00Z",
    )

    assert result["matchedHours"] == 1
    assert result["comparisons"][0]["forecastGeneration"] == 120
    assert result["comparisons"][0]["actualGeneration"] == 120
    assert result["mae"] == 0
    assert result["rmse"] == 0
    assert result["bias"] == 0


def test_excludes_incomplete_actual_hour():
    actuals = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "generation": 110,
        }
    ]

    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T09:30:00Z",
            "generation": 120,
        }
    ]

    result = evaluate_forecasts(
        actual_records=actuals,
        forecast_records=forecasts,
        delivery_date="2026-01-15",
        cutoff="2026-01-14T10:00:00Z",
    )

    assert result["matchedHours"] == 0
    assert result["mae"] is None


def test_duplicate_actual_half_hour_is_not_counted_twice():
    actuals = [
        {"startTime": "2026-01-15T00:00:00Z", "generation": 100},
        {"startTime": "2026-01-15T00:00:00Z", "generation": 100},
        # The distinct second half-hour is missing.
    ]
    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T09:00:00Z",
            "generation": 120,
        }
    ]

    result = evaluate_forecasts(
        actuals,
        forecasts,
        "2026-01-15",
        "2026-01-14T10:00:00Z",
    )

    assert result["matchedHours"] == 0
    assert result["mae"] is None


def test_non_finite_generation_values_are_rejected():
    actuals = [
        {"startTime": "2026-01-15T00:00:00Z", "generation": float("nan")},
        {"startTime": "2026-01-15T00:30:00Z", "generation": 100},
    ]
    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T09:00:00Z",
            "generation": float("inf"),
        }
    ]

    result = evaluate_forecasts(
        actuals,
        forecasts,
        "2026-01-15",
        "2026-01-14T10:00:00Z",
    )

    assert result["matchedHours"] == 0
    assert result["mae"] is None
    assert result["rmse"] is None
    assert result["bias"] is None
