import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(path, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    return requests.get(f"{BASE_URL}{path}", params=params).json()


def get_movie_full(tmdb_id):
    details = tmdb_get(f"/movie/{tmdb_id}")
    videos = tmdb_get(f"/movie/{tmdb_id}/videos")
    credits = tmdb_get(f"/movie/{tmdb_id}/credits")
    providers = tmdb_get(f"/movie/{tmdb_id}/watch/providers")
    similar = tmdb_get(f"/movie/{tmdb_id}/similar")

    # 🎬 Trailer (YouTube)
    trailer = None
    for v in videos.get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            trailer = v["key"]
            break

    # 👥 Cast (Top 10)
    cast = [
        {
            "id": c["id"],
            "name": c["name"],
            "character": c["character"],
            "profile_path": c["profile_path"]
        }
        for c in credits.get("cast", [])[:10]
    ]

    # 🎥 Director
    director = None
    for c in credits.get("crew", []):
        if c["job"] == "Director":
            director = c["name"]
            break

    # 📺 Providers
    providers_list = []
    india = providers.get("results", {}).get("IN", {})
    for p in india.get("flatrate", []):
        providers_list.append({
            "name": p["provider_name"],
            "logo_path": p["logo_path"]
        })

    return {
        "movie": {
            "id": details["id"],
            "title": details["title"],
            "overview": details["overview"],
            "poster_path": details["poster_path"],
            "backdrop_path": details["backdrop_path"],
            "genres": [g["name"] for g in details.get("genres", [])],
            "runtime": details.get("runtime"),
            "rating": details.get("vote_average"),
            "release_date": details.get("release_date"),
        },
        "trailer": trailer,
        "cast": cast,
        "director": director,
        "providers": providers_list,
        "similar": [
            {
                "id": s["id"],
                "title": s["title"],
                "poster_path": s["poster_path"]
            }
            for s in similar.get("results", [])[:10]
        ]
    }
