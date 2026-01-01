import { useEffect, useState, useContext } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

import Header from "../components/Header";
import Footer from "../components/Footer";
import MovieRow from "../components/MovieRow";
import ReviewCard from "../components/ReviewCard";
import { AuthContext } from "../context/AuthContext";

import "../styles/movieDetail.css";

export default function MovieDetail() {
  const { id } = useParams();            // TMDB ID (from URL)
  const { user } = useContext(AuthContext);

  const [movie, setMovie] = useState(null);
  const [trailer, setTrailer] = useState(null);
  const [cast, setCast] = useState([]);
  const [director, setDirector] = useState(null);
  const [providers, setProviders] = useState([]);
  const [similar, setSimilar] = useState([]);

  const [hybridRec, setHybridRec] = useState([]);
  const [crewRec, setCrewRec] = useState([]);

  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(0);
  const [reviewText, setReviewText] = useState("");
  const [status, setStatus] = useState({ watchlist: false, watched: false });

  /* -----------------------------------
     Fetch Reviews (INTERNAL ID)
  ------------------------------------*/
  const fetchReviews = (internalId) => {
    api.get(`/movie/${internalId}/reviews`)
      .then(r => setReviews(r.data || []))
      .catch(() => {});
  };

  /* -----------------------------------
     MAIN DATA LOADER
  ------------------------------------*/
  useEffect(() => {
    let mounted = true;

    async function loadMovie() {
      try {
        /* ---- 1. Movie Core (TMDB ID) ---- */
        const res = await api.get(`/movie/${id}`);
        if (!mounted) return;

        const data = res.data;
        setMovie(data.movie);
        setTrailer(data.trailer);
        setCast(data.cast || []);
        setDirector(data.director || null);
        setProviders(data.providers || []);
        setSimilar(data.similar || []);

        const internalId = data.movie.internal_id;

        /* ---- 2. Status (INTERNAL ID) ---- */
        api.get(`/movie/${internalId}/status`)
          .then(r => mounted && setStatus(r.data))
          .catch(() => {});

        /* ---- 3. Hybrid (INTERNAL ID) ---- */
        api.get(`/recommend/hybrid?movie_id=${internalId}`)
          .then(r => mounted && setHybridRec(r.data || []))
          .catch(() => {});

        /* ---- 4. Crew (TMDB ID ONLY) ---- */
        api.get(`/recommend/crew/${id}`)
          .then(r => mounted && setCrewRec(r.data || []))
          .catch(() => {});

        /* ---- 5. Reviews ---- */
        fetchReviews(internalId);

      } catch (err) {
        console.error("Movie load error:", err);
      }
    }

    loadMovie();
    return () => { mounted = false; };
  }, [id]);

  /* -----------------------------------
     ACTIONS
  ------------------------------------*/
  const toggleWatchlist = async () => {
    const res = await api.post("/watchlist/toggle", {
      movie_id: movie.internal_id
    });
    setStatus(s => ({ ...s, watchlist: res.data.status === "added" }));
  };

  const toggleWatched = async () => {
    const res = await api.post("/watched/toggle", {
      movie_id: movie.internal_id
    });
    setStatus({ watched: res.data.status === "added", watchlist: false });
  };

  const submitReview = async () => {
    if (!rating || !reviewText.trim()) return;

    await api.post("/review", {
      movie_id: movie.internal_id,
      rating,
      comment: reviewText
    });

    fetchReviews(movie.internal_id);
    setRating(0);
    setReviewText("");
  };

  /* -----------------------------------
     LOADING STATE
  ------------------------------------*/
  if (!movie) {
    return (
      <>
        <Header />
        <div className="loading-container">
          <p>Loading cinematic details…</p>
        </div>
        <Footer />
      </>
    );
  }

  /* -----------------------------------
     RENDER
  ------------------------------------*/
  return (
    <>
      <Header />

      <div className="movie-detail">
        {/* HERO */}
        <div className="movie-hero">
          <img
            src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
            alt={movie.title}
          />

          <div className="movie-info">
            <h1>{movie.title}</h1>

            {director && (
              <p className="director">
                Directed by: <span>{director}</span>
              </p>
            )}

            <p className="genres">{movie.genres.join(" • ")}</p>
            <p className="overview">{movie.overview}</p>

            {user && (
              <div className="actions">
                <button
                  onClick={toggleWatchlist}
                  className={status.watchlist ? "active" : ""}
                >
                  {status.watchlist ? "✔ In Watchlist" : "➕ Watchlist"}
                </button>

                <button
                  onClick={toggleWatched}
                  className={status.watched ? "active" : ""}
                >
                  {status.watched ? "✔ Watched" : "Mark Watched"}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* TRAILER */}
        {trailer && (
          <div className="section">
            <h2>🎬 Official Trailer</h2>
            <div className="video-wrapper">
              <iframe
                src={`https://www.youtube.com/embed/${trailer}`}
                title="Trailer"
                allowFullScreen
              />
            </div>
          </div>
        )}

        {/* PROVIDERS */}
        {providers.length > 0 && (
          <div className="section">
            <h2>📺 Where to Watch</h2>
            <div className="providers">
              {providers.map((p, i) => (
                <img
                  key={i}
                  src={`https://image.tmdb.org/t/p/w92${p.logo_path}`}
                  alt={p.name}
                  title={p.name}
                />
              ))}
            </div>
          </div>
        )}

        {/* CAST */}
        {cast.length > 0 && (
          <div className="section">
            <h2>👥 Top Cast</h2>
            <div className="cast-row">
              {cast.map(c => (
                <div className="cast-card" key={c.id}>
                  <img
                    src={
                      c.profile_path
                        ? `https://image.tmdb.org/t/p/w185${c.profile_path}`
                        : "https://via.placeholder.com/185x278?text=No+Image"
                    }
                    alt={c.name}
                  />
                  <p><strong>{c.name}</strong></p>
                  <p className="character">{c.character}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* REVIEWS */}
        <div className="section">
          <h2>⭐ User Reviews</h2>

          {user && (
            <div className="review-box">
              <div className="stars">
                {[1,2,3,4,5].map(s => (
                  <span
                    key={s}
                    className={s <= rating ? "star active" : "star"}
                    onClick={() => setRating(s)}
                  >
                    ★
                  </span>
                ))}
              </div>

              <textarea
                placeholder="Share your experience…"
                value={reviewText}
                onChange={e => setReviewText(e.target.value)}
              />

              <button className="btn-red" onClick={submitReview}>
                Submit Review
              </button>
            </div>
          )}

          <div className="reviews-container">
            {reviews.length === 0 ? (
              <p className="no-reviews">
                No reviews yet. Be the first to share your experience!
              </p>
            ) : (
              reviews.map(r => (
                <ReviewCard
                  key={r.id}
                  review={r}
                  currentUser={user}
                  onRefresh={() => fetchReviews(movie.internal_id)}
                />
              ))
            )}
          </div>
        </div>

        {/* RECOMMENDATIONS */}
        {hybridRec.length > 0 && (
          <MovieRow title="✨ Recommended For You" movies={hybridRec} />
        )}

        {crewRec.length > 0 && (
          <MovieRow title="🎬 More From Same Crew" movies={crewRec} />
        )}

        {similar.length > 0 && (
          <MovieRow title="🎯 Similar Movies" movies={similar} />
        )}
      </div>

      <Footer />
    </>
  );
}
