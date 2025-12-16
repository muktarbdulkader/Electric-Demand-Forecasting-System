import React, { useEffect, useState } from "react";
import { getRealtimeStatus, getRealtimeSummary, getPowerPlants, getRegionalDemand, RealtimeStatus, PowerPlant, RegionalData } from "../services/api";

const Realtime: React.FC = () => {
  const [status, setStatus] = useState<RealtimeStatus | null>(null);
  const [plants, setPlants] = useState<PowerPlant[]>([]);
  const [regions, setRegions] = useState<RegionalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      const [statusData, plantsData, regionsData] = await Promise.all([
        getRealtimeStatus(),
        getPowerPlants(),
        getRegionalDemand()
      ]);
      setStatus(statusData);
      setPlants(plantsData.plants);
      setRegions(regionsData.regions);
      setLastUpdate(new Date());
    } catch (err) {
      console.error("Failed to fetch realtime data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="loading">⚡ Loading Real-time Grid Data...</div>;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "operational": return "#10b981";
      case "maintenance": return "#f59e0b";
      case "offline": return "#ef4444";
      default: return "#6b7280";
    }
  };

  return (
    <div className="page realtime">
      <div className="page-header">
        <h1>⚡ Real-time Grid Status</h1>
        <div className="last-update">
          🔄 Last updated: {lastUpdate.toLocaleTimeString()}
          <button onClick={fetchData} className="refresh-btn">Refresh</button>
        </div>
      </div>

      {status && (
        <>
          <div className="grid-status-banner" data-status={status.grid_status}>
            <span className="status-indicator"></span>
            <span className="status-text">
              Grid Status: <strong>{status.grid_status.toUpperCase()}</strong>
            </span>
            <span className="frequency">Frequency: {status.frequency_hz} Hz</span>
          </div>

          <div className="stats-grid">
            <div className="stat-card highlight">
              <span className="stat-icon">⚡</span>
              <div className="stat-info">
                <span className="stat-value">{status.current_demand_mw.toLocaleString()}</span>
                <span className="stat-label">Current Demand (MW)</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🏭</span>
              <div className="stat-info">
                <span className="stat-value">{status.current_generation_mw.toLocaleString()}</span>
                <span className="stat-label">Generation (MW)</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon">📊</span>
              <div className="stat-info">
                <span className="stat-value">{status.reserve_margin_percent}%</span>
                <span className="stat-label">Reserve Margin</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🔌</span>
              <div className="stat-info">
                <span className="stat-value">{status.operational_capacity_mw.toLocaleString()}</span>
                <span className="stat-label">Available Capacity (MW)</span>
              </div>
            </div>
          </div>

          <div className="voltage-section">
            <h3>🔋 Voltage Levels</h3>
            <div className="voltage-cards">
              <div className="voltage-card">
                <span className="voltage-level">230 kV</span>
                <span className="voltage-value">{status.voltage_levels["230kV"]} kV</span>
                <span className="voltage-status normal">Normal</span>
              </div>
              <div className="voltage-card">
                <span className="voltage-level">132 kV</span>
                <span className="voltage-value">{status.voltage_levels["132kV"]} kV</span>
                <span className="voltage-status normal">Normal</span>
              </div>
              <div className="voltage-card">
                <span className="voltage-level">66 kV</span>
                <span className="voltage-value">{status.voltage_levels["66kV"]} kV</span>
                <span className="voltage-status normal">Normal</span>
              </div>
            </div>
          </div>
        </>
      )}

      <div className="power-plants-section">
        <h2>🏭 Power Plants Status</h2>
        <div className="plants-grid">
          {plants.slice(0, 8).map((plant) => (
            <div key={plant.name} className="plant-card">
              <div className="plant-header">
                <h4>{plant.name}</h4>
                <span 
                  className="plant-status" 
                  style={{ backgroundColor: getStatusColor(plant.status) }}
                >
                  {plant.status}
                </span>
              </div>
              <div className="plant-type">{plant.type} • {plant.location}</div>
              <div className="plant-stats">
                <div className="plant-output">
                  <span className="output-value">{plant.current_output_mw}</span>
                  <span className="output-label">/ {plant.capacity_mw} MW</span>
                </div>
                <div className="utilization-bar">
                  <div 
                    className="utilization-fill" 
                    style={{ width: `${plant.utilization_percent}%` }}
                  ></div>
                </div>
                <span className="utilization-text">{plant.utilization_percent}% utilized</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="regional-section">
        <h2>🗺️ Regional Demand</h2>
        <div className="regions-table">
          <table>
            <thead>
              <tr>
                <th>Region</th>
                <th>Current (MW)</th>
                <th>Peak (MW)</th>
                <th>Population</th>
                <th>Per Capita (kW)</th>
              </tr>
            </thead>
            <tbody>
              {regions.map((region) => (
                <tr key={region.region}>
                  <td><strong>{region.region}</strong></td>
                  <td>{region.current_demand_mw.toFixed(0)}</td>
                  <td>{region.peak_demand_mw.toFixed(0)}</td>
                  <td>{(region.population / 1000000).toFixed(1)}M</td>
                  <td>{region.per_capita_kw.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="info-section">
        <h3>ℹ️ About Ethiopian Electric Grid</h3>
        <div className="info-cards">
          <div className="info-card">
            <h4>💧 Hydropower Dominance</h4>
            <p>Over 90% of Ethiopia's electricity comes from hydropower, primarily from GERD, Gilgel Gibe, and Tekeze dams.</p>
          </div>
          <div className="info-card">
            <h4>🌍 Power Export</h4>
            <p>Ethiopia exports electricity to neighboring countries including Djibouti, Sudan, and Kenya.</p>
          </div>
          <div className="info-card">
            <h4>📈 Growing Demand</h4>
            <p>Electricity demand grows 10-15% annually as industrialization and urbanization increase.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Realtime;
