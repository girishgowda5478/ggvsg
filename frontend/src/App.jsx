
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import {
  Wind,
  Activity,
  Target,
  TrendingUp,
  RefreshCw,
  AlertCircle,
  CalendarDays,
} from "lucide-react";
import "./App.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "") + "/api";

function formatNumber(value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return "—";
  }

  return Number(value).toLocaleString("en-GB", {
    maximumFractionDigits: 1,
  });
}

function App() {
  const [monthData, setMonthData] = useState(null);
  const [dayData, setDayData] = useState(null);
  const [selectedDate, setSelectedDate] = useState("2026-01-15");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard(date = selectedDate) {
    setLoading(true);
    setError("");

    try {
      const [monthResponse, dayResponse] = await Promise.all([
        fetch(`${API_URL}/metrics?month=2026-01`),
        fetch(`${API_URL}/daily?date=${date}`),
      ]);

      if (!monthResponse.ok || !dayResponse.ok) {
        throw new Error(
          "The API returned an error. Check that the Python backend is running."
        );
      }

      const [month, day] = await Promise.all([
        monthResponse.json(),
        dayResponse.json(),
      ]);

      setMonthData(month);
      setDayData(day);
    } catch (err) {
      setError(
        `${err.message} Make sure FastAPI is running at http://127.0.0.1:8000.`
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
  let cancelled = false;

  async function loadInitialDashboard() {
    setLoading(true);
    setError("");

    try {
      const [monthResponse, dayResponse] = await Promise.all([
        fetch(`${API_URL}/metrics?month=2026-01`),
        fetch(`${API_URL}/daily?date=${selectedDate}`),
      ]);

      if (!monthResponse.ok || !dayResponse.ok) {
        throw new Error("The API returned an error. Check that the Python backend is running.");
      }

      const [month, day] = await Promise.all([
        monthResponse.json(),
        dayResponse.json(),
      ]);

      if (!cancelled) {
        setMonthData(month);
        setDayData(day);
      }
    } catch (err) {
      if (!cancelled) {
        setError(
          `${err.message} Make sure FastAPI is running at ${API_URL.replace(/\/api$/, "")}.`
        );
      }
    } finally {
      if (!cancelled) {
        setLoading(false);
      }
    }
  }

  loadInitialDashboard();

  return () => {
    cancelled = true;
  };
}, []);

  function handleDateChange(event) {
    const date = event.target.value;
    setSelectedDate(date);
    loadDashboard(date);
  }

  const chartData = (dayData?.comparisons ?? []).map((item) => ({
    time: new Date(item.startTime).toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "UTC",
    }),
    Forecast: Number(item.forecastGeneration),
    Actual: Number(item.actualGeneration),
  }));

  const kpis = [
    {
      label: "Monthly MAE",
      value: formatNumber(monthData?.mae),
      description: "Average absolute error",
      icon: Target,
    },
    {
      label: "Monthly RMSE",
      value: formatNumber(monthData?.rmse),
      description: "Penalises larger errors",
      icon: Activity,
    },
    {
      label: "Forecast bias",
      value: formatNumber(monthData?.bias),
      description: "Positive means over-forecasting",
      icon: TrendingUp,
    },
    {
      label: "Matched hours",
      value: monthData
        ? `${formatNumber(monthData.matchedHours)} / ${formatNumber(monthData.expectedHours)}`
        : "—",
      description: `${formatNumber(monthData?.coveragePercent)}% coverage`,
      icon: Wind,
    },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Wind size={24} />
          </div>
          <div>
            <h1>WindProcure</h1>
            <span>Forecast intelligence</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>
        <div className="nav-item active">
          <Activity size={18} />
          <span>Overview</span>
        </div>
        <div className="nav-item">
          <TrendingUp size={18} />
          <span>Forecast evaluation</span>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <span>January 2026 dataset</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">ENERGY ANALYTICS / OVERVIEW</div>
            <h2>Wind forecast performance</h2>
            <p>Compare day-ahead forecasts with observed wind generation.</p>
          </div>

          <button
            className="refresh-button"
            onClick={() => loadDashboard(selectedDate)}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? "spin" : ""} />
            Refresh data
          </button>
        </header>

        {error && (
          <div className="error-banner">
            <AlertCircle size={19} />
            <span>{error}</span>
          </div>
        )}

        <section className="notice">
          <AlertCircle size={18} />
          <div>
            <strong>Evaluation assumption</strong>
            <span>
              This dashboard uses an illustrative 09:20 UTC preceding-day forecast cutoff. Metrics are preliminary until the procurement deadline, forecast timing, and interval definitions are validated.
            </span>
          </div>
        </section>

        <section className="section-heading">
          <div>
            <h3>Monthly performance</h3>
            <p>January 1–31, 2026 · Elexon BMRS data</p>
          </div>
          <span className="period-pill">JAN 2026</span>
        </section>

        <section className="kpi-grid">
          {kpis.map((kpi) => {
            const Icon = kpi.icon;

            return (
              <article className="kpi-card" key={kpi.label}>
                <div className="kpi-top">
                  <span>{kpi.label}</span>
                  <div className="kpi-icon">
                    <Icon size={19} />
                  </div>
                </div>
                <div className="kpi-value">
                  {loading ? "…" : kpi.value}
                </div>
                <div className="kpi-description">{kpi.description}</div>
              </article>
            );
          })}
        </section>

        <section className="section-heading daily-heading">
          <div>
            <h3>Daily forecast vs actual</h3>
            <p>Hourly generation for the selected delivery date</p>
          </div>

          <label className="date-control">
            <CalendarDays size={17} />
            <input
              type="date"
              min="2026-01-01"
              max="2026-01-31"
              value={selectedDate}
              onChange={handleDateChange}
            />
          </label>
        </section>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <h4>Generation comparison</h4>
              <p>Forecast and actual generation by delivery hour</p>
            </div>
            {dayData && (
              <span className="matched-pill">
                {dayData.matchedHours} matched hours
              </span>
            )}
          </div>

          <div className="chart-area">
            {loading ? (
              <div className="empty-state">Loading forecast data…</div>
            ) : chartData.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{ top: 12, right: 18, left: 0, bottom: 4 }}
                >
                  <CartesianGrid stroke="#e8edf3" strokeDasharray="4 4" />
                  <XAxis
                    dataKey="time"
                    tick={{ fill: "#778397", fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    interval={3}
                  />
                  <YAxis
                    tick={{ fill: "#778397", fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    width={58}
                  />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="Forecast"
                    stroke="#4f6bed"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Actual"
                    stroke="#13a889"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                No matched hourly records were returned for this date.
              </div>
            )}
          </div>
        </section>

        <section className="bottom-grid">
          <article className="panel summary-panel">
            <h4>Selected-day evaluation</h4>
            <p className="panel-subtitle">
              Error = forecast generation − actual generation
            </p>

            <div className="summary-row">
              <span>Mean absolute error</span>
              <strong>{loading ? "…" : formatNumber(dayData?.mae)}</strong>
            </div>
            <div className="summary-row">
              <span>Root mean squared error</span>
              <strong>{loading ? "…" : formatNumber(dayData?.rmse)}</strong>
            </div>
            <div className="summary-row">
              <span>Forecast bias</span>
              <strong>{loading ? "…" : formatNumber(dayData?.bias)}</strong>
            </div>
            <div className="summary-row">
              <span>Matched delivery hours</span>
              <strong>
                {loading ? "…" : formatNumber(dayData?.matchedHours)}
              </strong>
            </div>
          </article>

          <article className="panel methodology-panel">
            <h4>How to read these metrics</h4>
            <div className="method-item">
              <span className="method-marker blue" />
              <div>
                <strong>MAE</strong>
                <p>Typical absolute difference between forecast and actual.</p>
              </div>
            </div>
            <div className="method-item">
              <span className="method-marker purple" />
              <div>
                <strong>RMSE</strong>
                <p>Highlights larger forecast errors more strongly.</p>
              </div>
            </div>
            <div className="method-item">
              <span className="method-marker green" />
              <div>
                <strong>Bias</strong>
                <p>Positive values indicate forecasts above actual generation.</p>
              </div>
            </div>
          </article>
        </section>

        <footer className="footer">
          <span>WindProcure · Forecast evaluation prototype</span>
          <span>Data source: Elexon BMRS API</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
