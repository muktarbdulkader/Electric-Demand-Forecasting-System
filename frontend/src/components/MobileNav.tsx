import React from "react";
import { NavLink } from "react-router-dom";

const MobileNav: React.FC = () => {
  return (
    <nav className="mobile-nav">
      <NavLink to="/" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`}>
        <span className="icon">📊</span>
        <span>Dashboard</span>
      </NavLink>
      <NavLink to="/forecast" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`}>
        <span className="icon">📈</span>
        <span>Forecast</span>
      </NavLink>
      <NavLink to="/realtime" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`}>
        <span className="icon">⚡</span>
        <span>Realtime</span>
      </NavLink>
      <NavLink to="/alerts" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`}>
        <span className="icon">🔔</span>
        <span>Alerts</span>
      </NavLink>
      <NavLink to="/ai-insights" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`}>
        <span className="icon">🤖</span>
        <span>AI</span>
      </NavLink>
    </nav>
  );
};

export default MobileNav;
