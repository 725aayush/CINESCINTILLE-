"""
User-Based Collaborative Filtering
----------------------------------
Uses ratings + watch history.
"""

from database.models import Review
from collections import defaultdict


def recommend_collaborative(user_id, top_n=10):
    # Movies rated by target user
    user_reviews = Review.query.filter_by(user_id=user_id).all()
    user_movies = {r.movie_id for r in user_reviews}

    if not user_movies:
        return []

    # Find similar users
    similar_users = defaultdict(int)

    all_reviews = Review.query.all()
    for r in all_reviews:
        if r.movie_id in user_movies and r.user_id != user_id:
            similar_users[r.user_id] += 1

    top_users = sorted(
        similar_users, key=similar_users.get, reverse=True
    )[:5]

    recommendations = defaultdict(int)

    for u in top_users:
        reviews = Review.query.filter_by(user_id=u).all()
        for r in reviews:
            if r.movie_id not in user_movies:
                recommendations[r.movie_id] += r.rating

    sorted_movies = sorted(
        recommendations, key=recommendations.get, reverse=True
    )

    return sorted_movies[:top_n]