import { useState } from "react";
import "./../styles/Slider.css";

export default function ProjectSlider() {
  const [index, setIndex] = useState(0);

  const slides = [
    { title: "Smart Discovery", desc: "Advanced Hybrid Algorithms for personalized picks.", img: "/static/project/slide1.png" },
    { title: "Global Cinema", desc: "Access thousands of titles from TMDB.", img: "/static/project/slide2.png" },
    { title: "Community Insights", desc: "See what other film buffs are watching.", img: "/static/project/slide3.png" },
    { title: "Your Watchlist", desc: "Organize your cinematic journey.", img: "/static/project/slide4.png" },
    { title: "Crew Analytics", desc: "Recommendations based on directors and writers.", img: "/static/project/slide5.png" }
  ];

  const next = () => setIndex((prev) => (prev + 1) % slides.length);
  const prev = () => setIndex((prev) => (prev - 1 + slides.length) % slides.length);

  return (
    <div className="slider project-hero">
      <div className="slide-content">
        <h2>{slides[index].title}</h2>
        <p>{slides[index].desc}</p>
      </div>
      <img src={slides[index].img} alt="Slide" className="slider-image" />
      <button className="slider-btn left" onClick={prev}>‹</button>
      <button className="slider-btn right" onClick={next}>›</button>
      <div className="overlay-vignette"></div>
    </div>
  );
}