import requests
import os
from dotenv import load_dotenv

from backend.app import create_app
from database.db import db
from database.models import Movie

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

app = create_app()


def fetch_popular_movies(page=1):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page
    }
    return requests.get(url, params=params).json().get("results", [])


def fetch_movie_credits(tmdb_id):
    url = f"{BASE_URL}/movie/{tmdb_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    return requests.get(url, params=params).json()


def extract_director_and_cast(credits):
    director = None
    cast_list = []

    # Director
    for person in credits.get("crew", []):
        if person.get("job") == "Director":
            director = person.get("name")
            break

    # Top 5 cast
    for actor in credits.get("cast", [])[:5]:
        cast_list.append(actor.get("name"))

    return director, ",".join(cast_list)


def seed_movies(pages=3):
    with app.app_context():
        for page in range(1, pages + 1):
            movies = fetch_popular_movies(page)

            for m in movies:
                if Movie.query.filter_by(tmdb_id=m["id"]).first():
                    continue

                credits = fetch_movie_credits(m["id"])
                director, cast = extract_director_and_cast(credits)

                movie = Movie(
                    tmdb_id=m["id"],
                    title=m["title"],
                    overview=m.get("overview"),
                    genres=",".join(map(str, m.get("genre_ids", []))),
                    release_date=m.get("release_date"),
                    poster_path=m.get("poster_path"),
                    popularity=m.get("popularity"),
                    language=m.get("original_language"),
                    director=director,
                    cast=cast
                )

                db.session.add(movie)

            db.session.commit()

        print("✅ Movies seeded with director & cast successfully")


if __name__ == "__main__":
    seed_movies(pages=3)
