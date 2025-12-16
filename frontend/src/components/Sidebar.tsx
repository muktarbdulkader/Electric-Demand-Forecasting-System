import React from "react";
import { Link, useLocation } from "react-router-dom";

const Sidebar: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    { path: "/", label: "Dashboard", icon: "📊" },
    { path: "/forecast", label: "Forecast", icon: "🔮" },
    { path: "/analytics", label: "Analytics", icon: "📈" },
    { path: "/households", label: "Households", icon: "🏠" },
    { path: "/ai", label: "AI Insights", icon: "🤖" },
    { path: "/realtime", label: "Real-time", icon: "📡" },
    { path: "/alerts", label: "Alerts", icon: "🔔" },
    { path: "/reports", label: "Reports", icon: "📋" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>Menu</h3>
      </div>
      <ul className="sidebar-menu">
        {menuItems.map((item) => (
          <li key={item.path}>
            <Link
              to={item.path}
              className={`sidebar-link ${location.pathname === item.path ? "active" : ""}`}
            >
              <span className="icon">{item.icon}</span>
              <span className="label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar;
