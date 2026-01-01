import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import axios from "axios";
import "./index.css";

/* 🔑 GLOBAL AXIOS CONFIG (VERY IMPORTANT) */
axios.defaults.baseURL = "http://localhost:5000";
axios.defaults.withCredentials = true;

const root = ReactDOM.createRoot(
  document.getElementById("root")
);

root.render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
