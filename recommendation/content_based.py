import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------
# Resolve artifact path safely (local + Render)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_PATH = os.path.join(BASE_DIR, "recommendation", "artifacts")


def load_artifacts():
    vectors_path = os.path.join(ARTIFACT_PATH, "movie_vectors.pkl")
    ids_path = os.path.join(ARTIFACT_PATH, "movie_ids.pkl")

    if not os.path.exists(vectors_path) or not os.path.exists(ids_path):
        # Fail safely — NEVER crash the server
        return None, None

    with open(vectors_path, "rb") as f:
        movie_vectors = pickle.load(f)

    with open(ids_path, "rb") as f:
        movie_ids = pickle.load(f)

    return movie_vectors, movie_ids


# -------------------------------------------------
# ✅ THIS is the function your app imports
# -------------------------------------------------
def recommend_similar_movies(movie_id, top_n=10):
    movie_vectors, movie_ids = load_artifacts()

    # Fail-safe fallback
    if movie_vectors is None or movie_ids is None:
        return []

    if movie_id not in movie_ids:
        return []

    idx = movie_ids.index(movie_id)
    query_vec = movie_vectors[idx].reshape(1, -1)

    similarities = cosine_similarity(query_vec, movie_vectors)[0]

    similar_indices = similarities.argsort()[::-1][1 : top_n + 1]

    return [movie_ids[i] for i in similar_indices]
