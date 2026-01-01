"""
Franchise-Based Recommendation
------------------------------
Recommends movies from the same franchise / series
"""

from database.models import Movie


def recommend_by_franchise(movie_id, top_n=10):
    movie = Movie.query.get(movie_id)
    if not movie or not movie.title:
        return []

    base_title = movie.title.split(":")[0].split("(")[0].strip().lower()

    similar_movies = Movie.query.filter(
        Movie.id != movie.id,
        Movie.title.ilike(f"%{base_title}%")
    ).limit(top_n).all()

    return [m.id for m in similar_movies]
