import React, { useState } from "react";
import axios from "axios";

interface ReportData {
  report_type: string;
  generated_at: string;
  summary?: {
    total_energy_mwh: number;
    peak_demand_mw: number;
    avg_daily_demand_mw?: number;
    peak_hour?: number;
    peak_day?: string;
  };
  hourly_data?: Array<{
    hour: number;
    avg_demand_mw: number;
    accuracy_percent: number;
  }>;
  daily_data?: Array<{
    date: string;
    avg_demand_mw: number;
    peak_demand_mw: number;
    total_energy_mwh: number;
  }>;
}

const Reports: React.FC = () => {
  const [reportType, setReportType] = useState<string>("daily");
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:8000/reports/${reportType}`);
      setReport(response.data);
    } catch (err) {
      setError("Failed to generate report. Please ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (format: string) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/reports/export/${format}?report_type=${reportType}`,
        { responseType: "blob" }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `eeu_report_${reportType}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Failed to export report");
    }
  };

  return (
    <div className="page reports">
      <h1>📋 Reports & Export</h1>

      <div className="report-controls" style={{ 
        display: "flex", 
        gap: "16px", 
        marginBottom: "24px",
        flexWrap: "wrap",
        alignItems: "center"
      }}>
        <div>
          <label style={{ marginRight: "8px" }}>Report Type:</label>
          <select 
            value={reportType} 
            onChange={(e) => setReportType(e.target.value)}
            style={{ padding: "8px 16px", borderRadius: "4px", border: "1px solid #d1d5db" }}
          >
            <option value="daily">Daily Report</option>
            <option value="weekly">Weekly Report</option>
            <option value="regional">Regional Report</option>
          </select>
        </div>
        
        <button 
          onClick={generateReport}
          disabled={loading}
          style={{
            padding: "8px 24px",
            background: "#059669",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "Generating..." : "Generate Report"}
        </button>

        <div style={{ marginLeft: "auto", display: "flex", gap: "8px" }}>
          <button 
            onClick={() => exportReport("csv")}
            style={{
              padding: "8px 16px",
              background: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            📥 Export CSV
          </button>
          <button 
            onClick={() => exportReport("json")}
            style={{
              padding: "8px 16px",
              background: "#7c3aed",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            📥 Export JSON
          </button>
        </div>
      </div>

      {error && (
        <div className="error-card" style={{ 
          padding: "16px", 
          background: "#fef2f2", 
          borderRadius: "8px",
          marginBottom: "16px",
          color: "#dc2626"
        }}>
          ⚠️ {error}
        </div>
      )}

      {report && (
        <div className="report-content">
          <div className="report-header" style={{
            padding: "16px",
            background: "#f0fdf4",
            borderRadius: "8px",
            marginBottom: "16px"
          }}>
            <h2 style={{ margin: "0 0 8px 0" }}>
              📊 {report.report_type.charAt(0).toUpperCase() + report.report_type.slice(1)} Report
            </h2>
            <p style={{ margin: 0, color: "#6b7280" }}>
              Generated: {new Date(report.generated_at).toLocaleString()}
            </p>
          </div>

          {report.summary && (
            <div className="stats-grid" style={{ marginBottom: "24px" }}>
              <div className="stat-card">
                <span className="stat-icon">⚡</span>
                <div className="stat-info">
                  <span className="stat-value">{report.summary.total_energy_mwh?.toLocaleString()}</span>
                  <span className="stat-label">Total Energy (MWh)</span>
                </div>
              </div>
              <div className="stat-card">
                <span className="stat-icon">📈</span>
                <div className="stat-info">
                  <span className="stat-value">{report.summary.peak_demand_mw?.toFixed(0)}</span>
                  <span className="stat-label">Peak Demand (MW)</span>
                </div>
              </div>
              {report.summary.avg_daily_demand_mw && (
                <div className="stat-card">
                  <span className="stat-icon">📊</span>
                  <div className="stat-info">
                    <span className="stat-value">{report.summary.avg_daily_demand_mw?.toFixed(0)}</span>
                    <span className="stat-label">Avg Daily (MW)</span>
                  </div>
                </div>
              )}
              {report.summary.peak_hour !== undefined && (
                <div className="stat-card">
                  <span className="stat-icon">🕐</span>
                  <div className="stat-info">
                    <span className="stat-value">{report.summary.peak_hour}:00</span>
                    <span className="stat-label">Peak Hour</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {report.hourly_data && (
            <div className="data-table" style={{ overflowX: "auto" }}>
              <h3>Hourly Breakdown</h3>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#f3f4f6" }}>
                    <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>Hour</th>
                    <th style={{ padding: "12px", textAlign: "right", borderBottom: "2px solid #e5e7eb" }}>Avg Demand (MW)</th>
                    <th style={{ padding: "12px", textAlign: "right", borderBottom: "2px solid #e5e7eb" }}>Accuracy (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {report.hourly_data.map((row) => (
                    <tr key={row.hour}>
                      <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>{row.hour}:00</td>
                      <td style={{ padding: "12px", textAlign: "right", borderBottom: "1px solid #e5e7eb" }}>
                        {row.avg_demand_mw.toFixed(0)}
                      </td>
                      <td style={{ padding: "12px", textAlign: "right", borderBottom: "1px solid #e5e7eb" }}>
                        <span style={{ color: row.accuracy_percent > 95 ? "#059669" : "#d97706" }}>
                          {row.accuracy_percent.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {report.daily_data && (
            <div className="data-table" style={{ overflowX: "auto" }}>
              <h3>Daily Breakdown</h3>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#f3f4f6" }}>
                    <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>Date</th>
                    <th style={{ padding: "12px", textAlign: "right", borderBottom: "2px solid #e5e7eb" }}>Avg (MW)</th>
                    <th style={{ padding: "12px", textAlign: "right", borderBottom: "2px solid #e5e7eb" }}>Peak (MW)</th>
                    <th style={{ padding: "12px", textAlign: "right", borderBottom: "2px solid #e5e7eb" }}>Energy (MWh)</th>
                  </tr>
                </thead>
                <tbody>
                  {report.daily_data.map((row) => (
                    <tr key={row.date}>
                      <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>{row.date}</td>
                      <td style={{ padding: "12px", textAlign: "right", borderBottom: "1px solid #e5e7eb" }}>
                        {row.avg_demand_mw.toFixed(0)}
                      </td>
                      <td style={{ padding: "12px", textAlign: "right", borderBottom: "1px solid #e5e7eb" }}>
                        {row.peak_demand_mw.toFixed(0)}
                      </td>
                      <td style={{ padding: "12px", textAlign: "right", borderBottom: "1px solid #e5e7eb" }}>
                        {row.total_energy_mwh.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {!report && !loading && (
        <div style={{ 
          padding: "60px", 
          textAlign: "center", 
          background: "#f9fafb", 
          borderRadius: "8px" 
        }}>
          <span style={{ fontSize: "48px" }}>📋</span>
          <h3>Generate a Report</h3>
          <p style={{ color: "#6b7280" }}>
            Select a report type and click "Generate Report" to view demand analytics
          </p>
        </div>
      )}
    </div>
  );
};

export default Reports;
