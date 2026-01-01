import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.models import Movie
from backend.app import create_app

def load_movies():
    """
    Fetch movies from database.
    Returns:
        movie_ids: list[int]
        documents: list[str]
    """
    app = create_app()

    with app.app_context():
        movies = Movie.query.all()

        movie_ids = []
        documents = []

        for movie in movies:
            text = ""
            if movie.genres:
                text += movie.genres.replace(",", " ") + " "
            if movie.overview:
                text += movie.overview

            movie_ids.append(movie.id)
            documents.append(text.lower())

    return movie_ids, documents
