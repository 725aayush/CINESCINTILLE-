import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity

ARTIFACT_PATH = os.path.join("recommendation", "artifacts")

def load_artifacts():
    with open(os.path.join(ARTIFACT_PATH, "movie_vectors.pkl"), "rb") as f:
        movie_vectors = pickle.load(f)

    with open(os.path.join(ARTIFACT_PATH, "movie_ids.pkl"), "rb") as f:
        movie_ids = pickle.load(f)

    return movie_vectors, movie_ids


def recommend_similar_movies(movie_id, top_n=10):
    movie_vectors, movie_ids = load_artifacts()

    if movie_id not in movie_ids:
        return []

    idx = movie_ids.index(movie_id)
    similarity_scores = cosine_similarity(
        movie_vectors[idx], movie_vectors
    ).flatten()

    similar_indices = similarity_scores.argsort()[::-1][1:top_n+1]

    return [movie_ids[i] for i in similar_indices]
