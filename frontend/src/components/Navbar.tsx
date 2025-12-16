import React from "react";
import { Link, useLocation } from "react-router-dom";
import { User } from "../services/api";

interface NavbarProps {
  user: User;
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Dashboard" },
    { path: "/forecast", label: "Forecast" },
    { path: "/analytics", label: "Analytics" },
    { path: "/households", label: "Households" },
    { path: "/ai", label: "AI Insights" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="logo">🇪🇹⚡</span>
        <span className="brand-text">Ethiopian Electric Utility</span>
      </div>
      <div className="navbar-links">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-link ${location.pathname === item.path ? "active" : ""}`}
          >
            {item.label}
          </Link>
        ))}
      </div>
      <div className="navbar-user">
        <span className="user-name">👤 {user.full_name}</span>
        <span className="user-region">{user.region}</span>
        <button onClick={onLogout} className="logout-btn">Logout</button>
      </div>
    </nav>
  );
};

export default Navbar;
