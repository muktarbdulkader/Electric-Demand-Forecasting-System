import React, { useEffect, useState } from "react";
import { createHousehold, getHouseholds, getHouseholdAnalytics, Household, HouseholdAnalytics, HouseholdCreate } from "../services/api";

const Households: React.FC = () => {
  const [households, setHouseholds] = useState<Household[]>([]);
  const [analytics, setAnalytics] = useState<HouseholdAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<HouseholdCreate>({
    name: "",
    address: "",
    region: "Addis Ababa",
    num_people: 4,
    num_rooms: 3,
    has_ac: false,
    has_heater: false,
    has_ev: false,
    appliances: []
  });

  const regions = [
    "Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNPR",
    "Somali", "Afar", "Benishangul-Gumuz", "Gambela", "Harari", "Dire Dawa"
  ];

  const appliances = ["Refrigerator", "TV", "Washing Machine", "Microwave", "Computer", "Water Heater"];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [householdsData, analyticsData] = await Promise.all([
        getHouseholds(),
        getHouseholdAnalytics()
      ]);
      setHouseholds(householdsData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createHousehold(formData);
      setShowForm(false);
      fetchData();
    } catch (err) {
      console.error("Failed to create household:", err);
    }
  };

  const toggleAppliance = (appliance: string) => {
    setFormData(prev => ({
      ...prev,
      appliances: prev.appliances.includes(appliance)
        ? prev.appliances.filter(a => a !== appliance)
        : [...prev.appliances, appliance]
    }));
  };

  if (loading) {
    return <div className="loading">Loading households...</div>;
  }

  return (
    <div className="page households">
      <h1>🏠 Household Management</h1>

      {analytics && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">🏘️</span>
            <div className="stat-info">
              <span className="stat-value">{analytics.total_households.toLocaleString()}</span>
              <span className="stat-label">Total Households</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">👥</span>
            <div className="stat-info">
              <span className="stat-value">{analytics.total_population.toLocaleString()}</span>
              <span className="stat-label">Total Population</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">⚡</span>
            <div className="stat-info">
              <span className="stat-value">{analytics.avg_consumption_kwh.toFixed(0)}</span>
              <span className="stat-label">Avg kWh/Month</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📈</span>
            <div className="stat-info">
              <span className="stat-value">{analytics.peak_demand_mw.toFixed(0)}</span>
              <span className="stat-label">Peak Demand (MW)</span>
            </div>
          </div>
        </div>
      )}

      <div className="section-header">
        <h2>Registered Households</h2>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Add Household"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="household-form">
          <div className="form-row">
            <div className="form-group">
              <label>Household Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Region</label>
              <select
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              >
                {regions.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Address</label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Number of People</label>
              <input
                type="number"
                min={1}
                value={formData.num_people}
                onChange={(e) => setFormData({ ...formData, num_people: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>Number of Rooms</label>
              <input
                type="number"
                min={1}
                value={formData.num_rooms}
                onChange={(e) => setFormData({ ...formData, num_rooms: Number(e.target.value) })}
              />
            </div>
          </div>

          <div className="form-row checkboxes">
            <label>
              <input
                type="checkbox"
                checked={formData.has_ac}
                onChange={(e) => setFormData({ ...formData, has_ac: e.target.checked })}
              />
              Air Conditioning
            </label>
            <label>
              <input
                type="checkbox"
                checked={formData.has_heater}
                onChange={(e) => setFormData({ ...formData, has_heater: e.target.checked })}
              />
              Electric Heater
            </label>
            <label>
              <input
                type="checkbox"
                checked={formData.has_ev}
                onChange={(e) => setFormData({ ...formData, has_ev: e.target.checked })}
              />
              Electric Vehicle
            </label>
          </div>

          <div className="form-group">
            <label>Appliances</label>
            <div className="appliances-grid">
              {appliances.map((a) => (
                <label key={a} className={formData.appliances.includes(a) ? "selected" : ""}>
                  <input
                    type="checkbox"
                    checked={formData.appliances.includes(a)}
                    onChange={() => toggleAppliance(a)}
                  />
                  {a}
                </label>
              ))}
            </div>
          </div>

          <button type="submit">Register Household</button>
        </form>
      )}

      <div className="households-list">
        {households.length === 0 ? (
          <p className="no-data">No households registered yet. Add one above!</p>
        ) : (
          households.map((h) => (
            <div key={h.id} className="household-card">
              <div className="household-header">
                <h3>{h.name}</h3>
                <span className="region-badge">{h.region}</span>
              </div>
              <p className="address">{h.address}</p>
              <div className="household-stats">
                <span>👥 {h.num_people} people</span>
                <span>🚪 {h.num_rooms} rooms</span>
                <span>⚡ {h.estimated_monthly_kwh} kWh/mo</span>
                <span>💰 {h.estimated_monthly_cost.toFixed(2)} Birr/mo</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Households;
