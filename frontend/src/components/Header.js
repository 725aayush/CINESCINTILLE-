import { useEffect, useState, useContext, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import { AuthContext } from "../context/AuthContext";
import "../styles/header.css";

export default function Header() {
  const { user, setUser } = useContext(AuthContext);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  const searchRef = useRef(null);
  const menuRef = useRef(null);

  const logout = async () => {
    await api.post("/logout");
    setUser(null);
    navigate("/login");
  };

  /* Close search on outside click */
  useEffect(() => {
    const handler = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setResults([]);
        setQuery("");
      }
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  /* Debounced search */
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const delay = setTimeout(() => {
      api.get(`/search?q=${query}`)
        .then(res => setResults(res.data))
        .catch(() => setResults([]));
    }, 350);
    return () => clearTimeout(delay);
  }, [query]);

  if (!user) return null;

  return (
    <header className="main-header">
      {/* LEFT */}
      <div className="header-left">
        <h1 className="logo" onClick={() => navigate("/home")}>
          CINESCINTILLE
        </h1>
      </div>

      {/* CENTER */}
      <div className="header-center">
        <div className="search-container" ref={searchRef}>
          <input
            className="search-input"
            placeholder="Search movies…"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          {results.length > 0 && (
            <div className="search-dropdown">
              {results.map(m => (
                <div
                  key={m.tmdb_id}
                  className="search-result-item"
                  onClick={() => {
                    navigate(`/movie/${m.tmdb_id}`);
                    setResults([]);
                    setQuery("");
                  }}
                >
                  {m.poster_path && (
                    <img
                      src={`https://image.tmdb.org/t/p/w92${m.poster_path}`}
                      alt={m.title}
                    />
                  )}
                  <span>{m.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT */}
      <div className="header-right">
        <div className="user-menu-wrapper" ref={menuRef}>
          <div
            className="profile-trigger"
            onClick={() => setShowDropdown(prev => !prev)}
          >
            <img
              src={`/static/avatars/${user.avatar}`}
              alt="Profile"
              className="header-avatar"
            />
            <span className="caret">▾</span>
          </div>

          {showDropdown && (
            <div className="profile-dropdown">
              <div className="dropdown-header">
                Hi, <strong>{user.username}</strong>
              </div>
              <Link
                to="/profile"
                className="dropdown-item"
                onClick={() => setShowDropdown(false)}
              >
                Your Profile
              </Link>
              <button
                className="dropdown-item logout-btn"
                onClick={logout}
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
