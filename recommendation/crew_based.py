"""
Crew-Based Recommendation
-------------------------
Recommends movies based on:
- Same director
- Overlapping cast
"""

from database.models import Movie
from collections import defaultdict


def recommend_by_crew(movie_id, top_n=10):
    scores = defaultdict(int)

    movie = Movie.query.get(movie_id)
    if not movie:
        return []

    # Director-based
    if movie.director:
        director_movies = Movie.query.filter(
            Movie.director == movie.director,
            Movie.id != movie.id
        ).all()

        for m in director_movies:
            scores[m.id] += 3

    # Cast-based
    if movie.cast:
        cast_members = set(a.strip() for a in movie.cast.split(","))

        all_movies = Movie.query.all()
        for m in all_movies:
            if not m.cast or m.id == movie.id:
                continue

            other_cast = set(a.strip() for a in m.cast.split(","))
            overlap = cast_members.intersection(other_cast)

            if overlap:
                scores[m.id] += len(overlap)

    ranked = sorted(scores, key=scores.get, reverse=True)
    return ranked[:top_n]
