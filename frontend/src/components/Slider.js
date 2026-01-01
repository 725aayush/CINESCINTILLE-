import { useState } from "react";
import "./../styles/Slider.css";

export default function Slider({ movies = [] }) {
  // ✅ Hooks FIRST (always)
  const [index, setIndex] = useState(0);

  // ✅ Guards AFTER hooks
  if (!Array.isArray(movies) || movies.length === 0) {
    return null;
  }

  const movie = movies[index];

  if (!movie || !movie.poster_path) {
    return null;
  }

  const next = () => {
    setIndex((prev) => (prev + 1) % movies.length);
  };

  const prev = () => {
    setIndex((prev) => (prev - 1 + movies.length) % movies.length);
  };

  return (
    <div className="slider">
      <button className="slider-btn left" onClick={prev}>
        ‹
      </button>

      <img
        src={`https://image.tmdb.org/t/p/w1280${movie.poster_path}`}
        alt={movie.title}
        className="slider-image"
      />

      <button className="slider-btn right" onClick={next}>
        ›
      </button>
    </div>
  );
}
