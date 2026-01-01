import axios from "axios";

const api = axios.create({
  baseURL: "https://cinescintille-backend.onrender.com",
  withCredentials: true,   //  REQUIRED
});

export default api;
