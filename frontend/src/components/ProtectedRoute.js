import { useContext, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api from "../api";
import { AuthContext } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, setUser } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // If already logged in → allow
    if (user) {
      setLoading(false);
      return;
    }

    // Check session
    api.get("/me")
      .then((res) => {
        if (res.data && res.data.id) {
          setUser(res.data);
        }
      })
      .finally(() => setLoading(false));
  }, [user, setUser]);

  if (loading) {
    return <p style={{ textAlign: "center" }}>Checking session...</p>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
