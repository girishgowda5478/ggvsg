# WindProcure — Wind Forecast Intelligence

A full-stack energy analytics dashboard for evaluating day-ahead wind generation forecasts against observed wind generation using Elexon BMRS data.

**Live application:** https://ggvsg.vercel.app/  
**Backend API:** https://ggvsg.onrender.com  
**Interactive API documentation:** https://ggvsg.onrender.com/docs

## Overview

WindProcure helps users examine the accuracy of wind generation forecasts and understand forecast errors through daily and monthly performance metrics.

The application retrieves forecast and actual wind generation data, aligns the records for evaluation, and presents the results through an interactive dashboard.

### Key features

- **Monthly performance metrics:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), forecast bias, and matched delivery hours.
- **Daily forecast evaluation:** Compare forecast and actual generation across delivery hours.
- **Interactive date selection:** Examine individual delivery dates within January 2026.
- **Data coverage reporting:** Review matched hours, missing hours, and coverage percentages.
- **REST API:** Access daily evaluation results and monthly performance metrics through FastAPI.
- **Evaluation transparency:** Document the assumed forecast cutoff and limitations affecting interpretation of the metrics.

## Technology stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Data visualization | Recharts |
| UI icons | Lucide React |
| Backend | Python, FastAPI |
| HTTP requests | Requests |
| Data source | Elexon BMRS API |
| Testing | Pytest |
| Backend deployment | Render |
| Frontend deployment | Vercel |

## Architecture

```text
Elexon BMRS API
      |
      v
FastAPI Backend (Render)
      |
      +-- /api/health
      +-- /api/daily
      +-- /api/metrics
      |
      v
React Frontend (Vercel)
      |
      v
Interactive Wind Forecast Dashboard
```

The backend retrieves the relevant source data, evaluates forecasts against actual generation, and returns JSON responses. The React frontend consumes these endpoints and displays the evaluation results.

## Evaluation methodology

### Data scope

- **Evaluation period:** January 1–31, 2026
- **Data source:** Elexon BMRS
- **Actual generation dataset:** `FUELHH`, filtered to wind generation
- **Forecast dataset:** `WINDFOR`
- **Evaluation interval:** Hourly
- **Expected delivery hours:** 744 for January 2026

### Forecast selection

The current implementation uses an illustrative cutoff of **09:20 UTC on the day before delivery**. For each delivery hour, it selects the latest eligible forecast record published at or before that cutoff.

This cutoff is an implementation assumption, not a confirmed requirement from the challenge brief. It must be validated against the applicable procurement deadline and forecast publication rules before the metrics are used for operational decisions.

### Actual generation alignment

The implementation deduplicates actual records by interval start time and averages the two half-hour generation values to calculate an hourly actual value. Incomplete hours without both distinct half-hour intervals are excluded from evaluation.

Forecast and actual interval definitions, units, and timestamp semantics should be independently validated before interpreting the results commercially.

### Evaluation metrics

Let \(F_i\) represent forecast generation and \(A_i\) represent actual generation for matched hour \(i\), with \(n\) matched hours.

**Mean Absolute Error (MAE)**

\[
MAE = \frac{1}{n}\sum_{i=1}^{n}|F_i-A_i|
\]

MAE measures the average absolute difference between forecast and actual generation.

**Root Mean Squared Error (RMSE)**

\[
RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(F_i-A_i)^2}
\]

RMSE penalizes larger forecast errors more strongly.

**Forecast bias**

\[
Bias = \frac{1}{n}\sum_{i=1}^{n}(F_i-A_i)
\]

Positive bias indicates that forecasts exceed actual generation on average; negative bias indicates under-forecasting.

**Coverage**

\[
Coverage = \frac{\text{Matched hours}}{\text{Expected hours}}\times100
\]

Coverage indicates the proportion of expected delivery hours included in the evaluation.

## API endpoints

The backend exposes the following endpoints.

| Endpoint | Description |
|---|---|
| `GET /api/health` | Checks backend health |
| `GET /api/daily?date=2026-01-15` | Returns evaluation results for a delivery date |
| `GET /api/metrics?month=2026-01` | Returns monthly evaluation metrics |

### Example requests

Health check:

```http
GET https://ggvsg.onrender.com/api/health
```

Daily evaluation:

```http
GET https://ggvsg.onrender.com/api/daily?date=2026-01-15
```

Monthly metrics:

```http
GET https://ggvsg.onrender.com/api/metrics?month=2026-01
```

Interactive API documentation is available at:

https://ggvsg.onrender.com/docs

## Local development

### Prerequisites

- Python 3.12 or a compatible Python version
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/girishgowda5478/ggvsg.git
cd ggvsg
```

### 2. Set up the backend

Create and activate a Python virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server from the repository root:

```powershell
uvicorn app.main:app --reload
```

The backend should be available at:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### 3. Set up the frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Create `frontend/.env.local` with the following value:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Start the frontend:

```powershell
npm run dev
```

Open the local URL displayed by Vite, usually:

http://localhost:5173

The backend's `FRONTEND_ORIGINS` environment variable must include the frontend origin when requests are made from a browser. For local development, the default configuration allows `http://localhost:5173` and `http://127.0.0.1:5173`.

### 4. Run backend tests

From the repository root, with the virtual environment activated:

```powershell
python -m pytest -q
```

The current backend test suite has four tests covering forecast selection, incomplete actual intervals, duplicate intervals, and invalid non-finite values.

### 5. Build and lint the frontend

From the `frontend` directory:

```powershell
npm run lint
npm run build
```

These commands check the frontend code and produce the production build.

## Deployment

The application is deployed as two services:

- **Frontend:** Vercel — https://ggvsg.vercel.app/
- **Backend:** Render — https://ggvsg.onrender.com

The frontend uses the `VITE_API_URL` environment variable to locate the backend API. In Vercel, this is configured as:

```text
VITE_API_URL=https://ggvsg.onrender.com
```

The backend uses `FRONTEND_ORIGINS` to configure the allowed browser origins. The deployed frontend origin must be included in this setting.

## Limitations and assumptions

- The evaluation is restricted to January 2026.
- The 09:20 UTC forecast cutoff is illustrative and requires validation.
- Forecast and actual generation interval semantics and units require independent confirmation.
- Incomplete actual hours are excluded from the matched evaluation set.
- Metrics describe the matched observations and should not be treated as proof of procurement savings or financial performance.
- The application is an evaluation prototype, not a production procurement or trading system.
- Render's free service may experience a delay on the first request after inactivity.

## Future improvements

- Validate procurement deadlines and forecast publication rules against authoritative documentation.
- Add configurable evaluation cutoffs and delivery periods.
- Improve handling and reporting of missing or invalid source records.
- Add historical comparisons across months and forecast publication cycles.
- Expand automated testing and data-quality monitoring.
- Introduce reproducible evaluation reports and downloadable results.

## Author

**Girish Gowda J**

GitHub: https://github.com/girishgowda5478

---

*WindProcure is a prototype developed to demonstrate full-stack application development, external energy-data integration, forecast evaluation, API design, testing, and deployment.*
