import { useRef } from "react";
import { Link } from "react-router-dom";
import "../styles/home.css";

export default function MovieRow({ title, movies = [] }) {
  const rowRef = useRef(null);

  if (!Array.isArray(movies) || movies.length === 0) {
    return null;
  }

  const scroll = (direction) => {
    const amount = direction === "left" ? -300 : 300;
    rowRef.current?.scrollBy({
      left: amount,
      behavior: "smooth"
    });
  };

  return (
    <section className="row">
      <h2>{title}</h2>

      <div className="row-wrapper">
        <button className="row-arrow left" onClick={() => scroll("left")}>
          ❮
        </button>

        <div className="row-posters" ref={rowRef}>
          {movies.map(movie => (
            <Link to={`/movie/${movie.id}`} key={movie.id}>
              <div className="movie-card">
                <img
                  src={`https://image.tmdb.org/t/p/w300${movie.poster_path}`}
                  alt={movie.title}
                />
                <div className="movie-overlay">
                  <p>{movie.title}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <button className="row-arrow right" onClick={() => scroll("right")}>
          ❯
        </button>
      </div>
    </section>
  );
}
