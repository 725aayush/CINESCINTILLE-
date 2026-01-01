from sklearn.feature_extraction.text import TfidfVectorizer

def build_vectorizer():
    return TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )
