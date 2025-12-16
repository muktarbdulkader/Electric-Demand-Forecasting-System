import React, { useState } from "react";
import { login, register, TokenResponse } from "../services/api";

interface LoginProps {
  onLogin: (user: TokenResponse) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [region, setRegion] = useState("Addis Ababa");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const regions = [
    "Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNPR",
    "Somali", "Afar", "Benishangul-Gumuz", "Gambela", "Harari", "Dire Dawa"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let response: TokenResponse;
      if (isRegister) {
        response = await register({ email, password, full_name: fullName, region });
      } else {
        response = await login({ email, password });
      }
      localStorage.setItem("token", response.access_token);
      localStorage.setItem("user", JSON.stringify(response.user));
      onLogin(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <span className="login-logo">🇪🇹⚡</span>
          <h1>Ethiopian Electric Utility</h1>
          <p>Demand Forecasting System</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <h2>{isRegister ? "Create Account" : "Sign In"}</h2>

          {error && <div className="login-error">{error}</div>}

          {isRegister && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  required
                />
              </div>
              <div className="form-group">
                <label>Region</label>
                <select value={region} onChange={(e) => setRegion(e.target.value)}>
                  {regions.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              minLength={6}
            />
          </div>

          <button type="submit" disabled={loading} className="login-btn">
            {loading ? "Please wait..." : isRegister ? "Create Account" : "Sign In"}
          </button>

          <p className="login-switch">
            {isRegister ? "Already have an account?" : "Don't have an account?"}
            <button type="button" onClick={() => setIsRegister(!isRegister)}>
              {isRegister ? "Sign In" : "Register"}
            </button>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
