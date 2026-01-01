import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import collageImg from "../assets/collage.png";
import "../styles/Auth.css";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    name: "",
    age: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await api.post("/register", form);

      // After successful registration → login page
      navigate("/login");
    } catch (err) {
      setError("Registration failed. Try a different username or email.");
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

        {/* Register form */}
        <div className="form-side">
          <div className="login-glass-card">
            <h2>Create Account</h2>

            {error && <div className="error-badge">{error}</div>}

            <form onSubmit={handleRegister} className="auth-form">
              <input
                name="username"
                placeholder="Username"
                value={form.username}
                onChange={handleChange}
                required
              />

              <input
                name="name"
                placeholder="Full Name"
                value={form.name}
                onChange={handleChange}
                required
              />

              <input
                name="age"
                type="number"
                placeholder="Age"
                value={form.age}
                onChange={handleChange}
              />

              <input
                name="email"
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={handleChange}
                required
              />

              <input
                name="password"
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
                required
              />

              <button type="submit" className="btn-primary">
                Register
              </button>
            </form>

            <p className="footer-link">
              Already have an account? <Link to="/login">Sign In</Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
