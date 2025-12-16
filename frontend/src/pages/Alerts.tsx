import React, { useEffect, useState } from "react";
import axios from "axios";

interface Alert {
  id: string;
  type: string;
  severity: string;
  title: string;
  message: string;
  recommendation: string;
  timestamp: string;
  acknowledged: boolean;
}

interface AlertSummary {
  total_alerts: number;
  unacknowledged: number;
  last_24h: {
    total: number;
    emergency: number;
    critical: number;
    warning: number;
  };
}

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<AlertSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    fetchAlerts();
    fetchSummary();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get("http://localhost:8000/alerts/");
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error("Failed to fetch alerts:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await axios.get("http://localhost:8000/alerts/summary");
      setSummary(response.data);
    } catch (error) {
      console.error("Failed to fetch summary:", error);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await axios.post(`http://localhost:8000/alerts/${alertId}/acknowledge`);
      fetchAlerts();
      fetchSummary();
    } catch (error) {
      console.error("Failed to acknowledge alert:", error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "emergency": return "#dc2626";
      case "critical": return "#ea580c";
      case "warning": return "#d97706";
      default: return "#059669";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "emergency": return "🚨";
      case "critical": return "⚠️";
      case "warning": return "📈";
      default: return "ℹ️";
    }
  };

  const filteredAlerts = filter === "all" 
    ? alerts 
    : alerts.filter(a => a.severity === filter);

  if (loading) {
    return <div className="loading">Loading alerts...</div>;
  }

  return (
    <div className="page alerts">
      <h1>🔔 Alerts & Notifications</h1>

      {summary && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">📊</span>
            <div className="stat-info">
              <span className="stat-value">{summary.total_alerts}</span>
              <span className="stat-label">Total Alerts</span>
            </div>
          </div>
          <div className="stat-card" style={{ borderLeft: "4px solid #dc2626" }}>
            <span className="stat-icon">🚨</span>
            <div className="stat-info">
              <span className="stat-value">{summary.last_24h.emergency}</span>
              <span className="stat-label">Emergency (24h)</span>
            </div>
          </div>
          <div className="stat-card" style={{ borderLeft: "4px solid #ea580c" }}>
            <span className="stat-icon">⚠️</span>
            <div className="stat-info">
              <span className="stat-value">{summary.last_24h.critical}</span>
              <span className="stat-label">Critical (24h)</span>
            </div>
          </div>
          <div className="stat-card" style={{ borderLeft: "4px solid #d97706" }}>
            <span className="stat-icon">📈</span>
            <div className="stat-info">
              <span className="stat-value">{summary.unacknowledged}</span>
              <span className="stat-label">Unacknowledged</span>
            </div>
          </div>
        </div>
      )}

      <div className="filter-section" style={{ margin: "20px 0" }}>
        <label>Filter by severity: </label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="emergency">Emergency</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>

      <div className="alerts-list">
        {filteredAlerts.length === 0 ? (
          <div className="no-alerts" style={{ padding: "40px", textAlign: "center", background: "#f0fdf4", borderRadius: "8px" }}>
            <span style={{ fontSize: "48px" }}>✅</span>
            <h3>No alerts</h3>
            <p>All systems operating normally</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className="alert-card"
              style={{
                padding: "16px",
                marginBottom: "12px",
                borderRadius: "8px",
                background: alert.acknowledged ? "#f9fafb" : "#fff",
                borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <h3 style={{ margin: "0 0 8px 0" }}>
                    {getSeverityIcon(alert.severity)} {alert.title}
                  </h3>
                  <p style={{ margin: "0 0 8px 0", color: "#4b5563" }}>{alert.message}</p>
                  <p style={{ margin: "0", fontSize: "14px", color: "#059669" }}>
                    💡 {alert.recommendation}
                  </p>
                  <p style={{ margin: "8px 0 0 0", fontSize: "12px", color: "#9ca3af" }}>
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
                {!alert.acknowledged && (
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    style={{
                      padding: "8px 16px",
                      background: "#059669",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer"
                    }}
                  >
                    Acknowledge
                  </button>
                )}
                {alert.acknowledged && (
                  <span style={{ color: "#059669", fontSize: "14px" }}>✓ Acknowledged</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Alerts;
