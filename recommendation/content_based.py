import os
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_PATH = os.path.join(BASE_DIR, "recommendation", "artifacts")

def load_artifacts():
    with open(os.path.join(ARTIFACT_PATH, "movie_vectors.pkl"), "rb") as f:
        movie_vectors = pickle.load(f)

    with open(os.path.join(ARTIFACT_PATH, "movie_ids.pkl"), "rb") as f:
        movie_ids = pickle.load(f)

    return movie_vectors, movie_ids
