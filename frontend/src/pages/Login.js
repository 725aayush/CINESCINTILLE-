import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import { AuthContext } from "../context/AuthContext";
import collageImg from "../assets/collage.png";
import "../styles/Auth.css";

export default function Login() {
  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await api.post("/login", {
        username,
        password
      });

      // Save user in global context
      setUser(res.data);

      // Redirect to home
      navigate("/home");
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-page">
      {/* Header */}
      <header className="main-header">
        <h1 className="brand-logo">CINESCINTILLE</h1>
      </header>

      <main className="split-container">
        {/* Left side image */}
        <div className="visual-side">
          <img src={collageImg} alt="Movies" className="collage-hero" />
          <div className="overlay-gradient"></div>
        </div>

        {/* Login form */}
        <div className="form-side">
          <div className="login-glass-card">
            <h2>Welcome Back</h2>

            {error && <div className="error-badge">{error}</div>}

            <form onSubmit={handleLogin} className="auth-form">
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />

              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <button type="submit" className="btn-primary">
                Sign In
              </button>
            </form>

            <p className="footer-link">
              New here? <Link to="/register">Create an account</Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
