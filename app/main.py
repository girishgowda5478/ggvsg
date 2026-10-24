
import os
from datetime import date, timedelta
from math import sqrt

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.data_service import load_january_data
from app.evaluation import evaluate_forecasts


app = FastAPI(
    title="WindProcure API",
    description="UK wind generation forecast accuracy analytics",
    version="1.0.0",
)

# Add deployed frontend origins through the FRONTEND_ORIGINS
# environment variable, separated by commas.
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def purchasing_cutoff(delivery_date: date) -> str:
    """Return the assumed 09:20 UTC deadline on the preceding day."""
    previous_day = delivery_date - timedelta(days=1)
    return f"{previous_day.isoformat()}T09:20:00Z"


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "WindProcure API",
    }


@app.get("/api/daily")
def daily(
    delivery_date: date = Query(
        ...,
        alias="date",
        description="Delivery date in January 2026",
    ),
):
    if delivery_date.year != 2026 or delivery_date.month != 1:
        raise HTTPException(
            status_code=400,
            detail="Only January 2026 is supported.",
        )

    try:
        actuals, forecasts = load_january_data()

        return evaluate_forecasts(
            actual_records=actuals,
            forecast_records=forecasts,
            delivery_date=delivery_date.isoformat(),
            cutoff=purchasing_cutoff(delivery_date),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Historical Elexon data retrieval failed: {exc}",
        ) from exc


@app.get("/api/metrics")
def metrics(
    month: str = Query(
        default="2026-01",
        pattern=r"^2026-01$",
    ),
):
    try:
        actuals, forecasts = load_january_data()

        all_comparisons = []
        daily_results = []

        for day in range(1, 32):
            delivery_date = date(2026, 1, day)

            result = evaluate_forecasts(
                actual_records=actuals,
                forecast_records=forecasts,
                delivery_date=delivery_date.isoformat(),
                cutoff=purchasing_cutoff(delivery_date),
            )

            all_comparisons.extend(result["comparisons"])

            daily_results.append({
                "date": delivery_date.isoformat(),
                "matchedHours": result["matchedHours"],
                "expectedHours": result["expectedHours"],
                "missingHours": result["missingHours"],
                "coveragePercent": result["coveragePercent"],
                "mae": result["mae"],
                "rmse": result["rmse"],
                "bias": result["bias"],
            })

        errors = [row["error"] for row in all_comparisons]
        count = len(errors)
        expected_hours = 31 * 24

        return {
            "month": month,
            "cutoffAssumption": (
                "09:20 UTC on the preceding day; "
                "assumed EPEX day-ahead auction deadline"
            ),
            "matchedHours": count,
            "expectedHours": expected_hours,
            "missingHours": expected_hours - count,
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
            "daily": daily_results,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Monthly evaluation failed: {exc}",
        ) from exc
