import { useEffect, useState } from "react";
import api from "../api";

import Header from "../components/Header";
import Footer from "../components/Footer";
import ProjectSlider from "../components/ProjectSlider";
import MovieRow from "../components/MovieRow";

import "../styles/home.css";

export default function Home() {
  const [popular, setPopular] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [collab, setCollab] = useState([]);
  const [content, setContent] = useState([]);
  const [crew, setCrew] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadHome() {
      try {
        setLoading(true);

        /* ===============================
           1. GLOBAL / STATIC ROWS
        =============================== */

        const homeRes = await api.get("/home");
        if (!mounted) return;

        const popularMovies = homeRes.data?.popular || [];
        setPopular(popularMovies);

        const topRatedRes = await api.get("/recommend/top-rated");
        setTopRated(topRatedRes.data || []);

        const collabRes = await api.get("/recommend/collaborative");
        setCollab(collabRes.data || []);

        /* ===============================
           2. DETERMINE SEED (TMDB ID)
        =============================== */

        let seedTmdbId = null;

        const watchedRes = await api.get("/profile/watched");

        if (watchedRes.data && watchedRes.data.length > 0) {
          // MOST RECENT watched movie (TMDB ID)
          seedTmdbId = watchedRes.data[watchedRes.data.length - 1].tmdb_id;
        } else if (popularMovies.length > 0) {
          // FALLBACK: first popular movie (TMDB ID)
          seedTmdbId = popularMovies[0].id;
        }

        /* ===============================
           3. DYNAMIC RECOMMENDATIONS
        =============================== */

        if (seedTmdbId) {
          const [contentRes, crewRes] = await Promise.all([
            api.get(`/recommend/content/${seedTmdbId}`),
            api.get(`/recommend/crew/${seedTmdbId}`)
          ]);

          if (mounted) {
            setContent(contentRes.data || []);
            setCrew(crewRes.data || []);
          }
        } else {
          // No valid seed — hide safely
          setContent([]);
          setCrew([]);
        }

      } catch (err) {
        console.error("Home load error:", err);
        if (mounted) {
          setError("Session expired or network error. Please login again.");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadHome();
    return () => { mounted = false; };
  }, []);

  /* ===============================
     UI STATES
  =============================== */

  if (loading) {
    return (
      <div className="home-container">
        <Header />
        <p className="loading">Loading recommendations…</p>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-container">
        <Header />
        <p className="error-message">{error}</p>
        <Footer />
      </div>
    );
  }

  /* ===============================
     MAIN RENDER
  =============================== */

  return (
    <div className="home-container">
      <Header />

      <ProjectSlider />

      <div className="home-content-sections">

        {/* TRENDING */}
        <div className="home-section-block">
          <div className="section-accent"></div>
          <MovieRow title="🔥 Trending Now" movies={popular} />
        </div>

        {/* TOP RATED */}
        {topRated.length > 0 && (
          <div className="home-section-block highlight-row">
            <div className="section-accent"></div>
            <MovieRow
              title="🏆 IMDb Top Gems (Unwatched)"
              movies={topRated}
            />
          </div>
        )}

        {/* COLLABORATIVE */}
        {collab.length > 0 && (
          <div className="home-section-block">
            <div className="section-accent"></div>
            <MovieRow
              title="👥 Community Favorites"
              movies={collab}
            />
          </div>
        )}

        {/* CONTENT BASED */}
        {content.length > 0 && (
          <div className="home-section-block">
            <div className="section-accent"></div>
            <MovieRow
              title="🎭 Because You Watched Something Like This"
              movies={content}
            />
          </div>
        )}

        {/* CREW BASED */}
        {crew.length > 0 && (
          <div className="home-section-block">
            <div className="section-accent"></div>
            <MovieRow
              title="🎬 From the Same Creative Team"
              movies={crew}
            />
          </div>
        )}

      </div>

      <Footer />
    </div>
  );
}
