import React, { useEffect, useState } from "react";
import ChartCard from "../components/ChartCard";
import UploadData from "../components/UploadData";
import { getAnalytics, get24hForecast, AnalyticsResponse, HourlyForecast } from "../services/api";

const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [forecasts, setForecasts] = useState<HourlyForecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsData, forecastData] = await Promise.all([
          getAnalytics(),
          get24hForecast(25),
        ]);
        setAnalytics(analyticsData);
        setForecasts(forecastData.forecasts);
        setError(null);
      } catch (err) {
        setError("Unable to connect to server. Please ensure backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  const formatHour = (h: number) => `${h}:00`;

  return (
    <div className="page analytics">
      <h1>📊 Analytics</h1>

      {error && <div className="error-card">⚠️ {error}</div>}

      {analytics && (
        <div className="analytics-grid">
          <div className="analytics-card">
            <span className="analytics-label">Average Demand</span>
            <span className="analytics-value">{analytics.avg_demand.toFixed(0)} MW</span>
          </div>
          <div className="analytics-card highlight-high">
            <span className="analytics-label">Peak Demand</span>
            <span className="analytics-value">{analytics.max_demand.toFixed(0)} MW</span>
            <span className="analytics-sub">at {formatHour(analytics.peak_hour)}</span>
          </div>
          <div className="analytics-card highlight-low">
            <span className="analytics-label">Minimum Demand</span>
            <span className="analytics-value">{analytics.min_demand.toFixed(0)} MW</span>
            <span className="analytics-sub">at {formatHour(analytics.low_hour)}</span>
          </div>
        </div>
      )}

      <div className="charts-section">
        {forecasts.length > 0 && (
          <ChartCard
            title="Demand Distribution (24h)"
            labels={forecasts.map((f) => `${f.hour}:00`)}
            data={forecasts.map((f) => f.predicted_demand)}
            type="bar"
            color="#d97706"
          />
        )}
      </div>

      <div className="upload-section">
        <UploadData />
      </div>
    </div>
  );
};

export default Analytics;
