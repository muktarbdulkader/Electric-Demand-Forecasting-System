import React, { useEffect, useState } from "react";
import ChartCard from "../components/ChartCard";
import { get24hForecast, HourlyForecast, getForecast } from "../services/api";

const Dashboard: React.FC = () => {
  const [forecasts, setForecasts] = useState<HourlyForecast[]>([]);
  const [currentDemand, setCurrentDemand] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [forecast24h, current] = await Promise.all([
          get24hForecast(25),
          getForecast(),
        ]);
        setForecasts(forecast24h.forecasts);
        setCurrentDemand(current.forecasted_demand);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch data:", err);
        setError("Unable to connect to server. Please ensure backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading Ethiopian Electric Dashboard...</div>;
  }

  if (error) {
    return (
      <div className="page dashboard">
        <h1>Dashboard</h1>
        <div className="error-card">
          <p>⚠️ {error}</p>
          <p>Run: <code>cd backend && uvicorn app.main:app --reload</code></p>
        </div>
      </div>
    );
  }

  const labels = forecasts.map((f) => `${f.hour}:00`);
  const demandData = forecasts.map((f) => f.predicted_demand);
  const tempData = forecasts.map((f) => f.temperature);

  const peakDemand = demandData.length > 0 ? Math.max(...demandData) : 0;
  const minDemand = demandData.length > 0 ? Math.min(...demandData) : 0;

  return (
    <div className="page dashboard">
      <h1>🇪🇹 Ethiopian Electric Utility - Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon">⚡</span>
          <div className="stat-info">
            <span className="stat-value">{currentDemand?.toFixed(0) ?? "--"}</span>
            <span className="stat-label">Current Demand (MW)</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">📈</span>
          <div className="stat-info">
            <span className="stat-value">{peakDemand.toFixed(0)}</span>
            <span className="stat-label">Peak Demand (MW)</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">📉</span>
          <div className="stat-info">
            <span className="stat-value">{minDemand.toFixed(0)}</span>
            <span className="stat-label">Min Demand (MW)</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">🌡️</span>
          <div className="stat-info">
            <span className="stat-value">25°C</span>
            <span className="stat-label">Avg Temperature</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <ChartCard
          title="24-Hour Demand Forecast (MW)"
          labels={labels}
          data={demandData}
          type="line"
          color="#059669"
        />
        <ChartCard
          title="Temperature Profile (°C)"
          labels={labels}
          data={tempData}
          type="bar"
          color="#d97706"
        />
      </div>
    </div>
  );
};

export default Dashboard;
