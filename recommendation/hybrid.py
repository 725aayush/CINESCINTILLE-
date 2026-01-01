"""
Hybrid Recommendation Engine
----------------------------
Combines multiple recommenders
"""

from collections import defaultdict
from database.models import Movie
from recommendation.content_based import recommend_similar_movies
from recommendation.collaborative import recommend_collaborative
from recommendation.crew_based import recommend_by_crew
from recommendation.franchise import recommend_by_franchise


def hybrid_recommendation(movie_id=None, user_id=None, top_n=10):
    scores = defaultdict(float)

    if movie_id:
        for m in recommend_similar_movies(movie_id, top_n=15):
            scores[m] += 0.4

        for m in recommend_by_franchise(movie_id):
            scores[m] += 0.3

        for m in recommend_by_crew(movie_id):
            scores[m] += 0.25

    if user_id:
        for m in recommend_collaborative(user_id):
            scores[m] += 0.2

    popular = Movie.query.order_by(Movie.popularity.desc()).limit(10).all()
    for m in popular:
        scores[m.id] += 0.1

    ranked = sorted(scores, key=scores.get, reverse=True)
    return ranked[:top_n]
