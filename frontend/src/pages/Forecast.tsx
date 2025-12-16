import React, { useState } from "react";
import ChartCard from "../components/ChartCard";
import { postForecast, get24hForecast, HourlyForecast } from "../services/api";

const Forecast: React.FC = () => {
  const [temperature, setTemperature] = useState(25);
  const [hour, setHour] = useState(new Date().getHours());
  const [dayOfWeek, setDayOfWeek] = useState(new Date().getDay());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [result, setResult] = useState<number | null>(null);
  const [forecasts, setForecasts] = useState<HourlyForecast[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await postForecast({
        temperature,
        hour,
        day_of_week: dayOfWeek,
        month,
      });
      setResult(response.forecasted_demand);
    } catch (err) {
      setError("Failed to get prediction. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleGet24h = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await get24hForecast(temperature);
      setForecasts(response.forecasts);
    } catch (err) {
      setError("Failed to get 24h forecast. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  return (
    <div className="page forecast">
      <h1>🔮 Demand Forecast</h1>

      <div className="forecast-form">
        <div className="form-group">
          <label>Temperature (°C)</label>
          <input
            type="number"
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
            min={10}
            max={45}
          />
        </div>
        <div className="form-group">
          <label>Hour (0-23)</label>
          <input
            type="number"
            min={0}
            max={23}
            value={hour}
            onChange={(e) => setHour(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Day of Week</label>
          <select value={dayOfWeek} onChange={(e) => setDayOfWeek(Number(e.target.value))}>
            {days.map((day, i) => (
              <option key={i} value={i}>{day}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Month</label>
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
            {months.map((m, i) => (
              <option key={i} value={i + 1}>{m}</option>
            ))}
          </select>
        </div>

        <div className="form-actions">
          <button onClick={handlePredict} disabled={loading}>
            {loading ? "Predicting..." : "Predict Single Hour"}
          </button>
          <button onClick={handleGet24h} disabled={loading} className="secondary">
            {loading ? "Loading..." : "Get 24h Forecast"}
          </button>
        </div>
      </div>

      {error && <div className="error-card">⚠️ {error}</div>}

      {result !== null && (
        <div className="result-card">
          <h3>Predicted Demand</h3>
          <span className="result-value">{result.toFixed(2)} MW</span>
        </div>
      )}

      {forecasts.length > 0 && (
        <ChartCard
          title="24-Hour Forecast (MW)"
          labels={forecasts.map((f) => `${f.hour}:00`)}
          data={forecasts.map((f) => f.predicted_demand)}
          type="line"
          color="#059669"
        />
      )}
    </div>
  );
};

export default Forecast;
