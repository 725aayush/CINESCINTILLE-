import pickle
import os

from recommendation.data_loader import load_movies
from recommendation.preprocess import build_vectorizer

ARTIFACT_PATH = os.path.join("recommendation", "artifacts")
os.makedirs(ARTIFACT_PATH, exist_ok=True)

def train():
    print("Loading movies from database...")
    movie_ids, documents = load_movies()

    print("Building TF-IDF vectors...")
    vectorizer = build_vectorizer()
    movie_vectors = vectorizer.fit_transform(documents)

    with open(os.path.join(ARTIFACT_PATH, "movie_vectors.pkl"), "wb") as f:
        pickle.dump(movie_vectors, f)

    with open(os.path.join(ARTIFACT_PATH, "movie_ids.pkl"), "wb") as f:
        pickle.dump(movie_ids, f)

    with open(os.path.join(ARTIFACT_PATH, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    print("✅ Content-based model trained successfully")

if __name__ == "__main__":
    train()
