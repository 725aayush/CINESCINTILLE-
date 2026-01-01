from flask import Blueprint, request, jsonify, session
from database.db import db
from database.models import User, Movie, Review, Watchlist, Watched
import requests
import os

from recommendation.hybrid import hybrid_recommendation
from recommendation.content_based import recommend_similar_movies
from recommendation.collaborative import recommend_collaborative
from recommendation.crew_based import recommend_by_crew
from .tmdb_service import get_movie_full

main = Blueprint("main", __name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"


# ======================================================
# HELPERS
# ======================================================

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def tmdb_get(path, params=None):
    params = params or {}
    params["api_key"] = TMDB_API_KEY
    return requests.get(f"{TMDB_BASE}{path}", params=params).json()


# ======================================================
# AUTH
# ======================================================

@main.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    if not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter(
        (User.username == data["username"]) |
        (User.email == data["email"])
    ).first():
        return jsonify({"error": "User already exists"}), 409

    user = User(
        username=data["username"],
        email=data["email"],
        name=data.get("name"),
        age=data.get("age"),
        avatar="default.jpg"
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id

    return jsonify({"id": user.id, "username": user.username}), 201


@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()

    if not user or not user.check_password(data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "name": user.name,
    "age": user.age,
    "avatar": user.avatar
    })


@main.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@main.route("/me")
def me():
    u = current_user()
    if not u:
        return jsonify({"user": None})

    return jsonify({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "name": u.name,
        "age": u.age,
        "avatar": u.avatar
    })


# ======================================================
# HOME (DYNAMIC)
# ======================================================

@main.route("/home")
def home():
    res = tmdb_get("/trending/movie/week")

    movies = []
    for m in res.get("results", [])[:20]:
        movie = Movie.query.filter_by(tmdb_id=m["id"]).first()
        if not movie:
            movie = Movie(
                tmdb_id=m["id"],
                title=m["title"],
                poster_path=m.get("poster_path", ""),
                popularity=m.get("popularity", 0)
            )
            db.session.add(movie)
        movies.append(movie)

    db.session.commit()

    def serialize(m):
        return {
            "id": m.tmdb_id,
            "title": m.title,
            "poster_path": m.poster_path
        }

    return jsonify({
        "hero": [serialize(m) for m in movies[:5]],
        "popular": [serialize(m) for m in movies]
    })


# ======================================================
# MOVIE DETAIL
# ======================================================

@main.route("/movie/<int:id>")
def movie_detail(id):
    movie = Movie.query.filter_by(tmdb_id=id).first()

    if not movie:
        tmdb_data = tmdb_get(f"/movie/{id}")
        if "id" not in tmdb_data:
            return jsonify({"error": "Movie not found"}), 404

        movie = Movie(
            tmdb_id=id,
            title=tmdb_data["title"],
            overview=tmdb_data.get("overview", ""),
            poster_path=tmdb_data.get("poster_path", ""),
            genres=",".join(g["name"] for g in tmdb_data.get("genres", [])),
            popularity=tmdb_data.get("popularity", 0)
        )
        db.session.add(movie)
        db.session.commit()

    full_data = get_movie_full(id)
    full_data["movie"]["internal_id"] = movie.id
    return jsonify(full_data)


@main.route("/movie/<int:id>/status")
def movie_status(id):
    u = current_user()
    if not u:
        return jsonify({"watchlist": False, "watched": False})

    return jsonify({
        "watchlist": Watchlist.query.filter_by(user_id=u.id, movie_id=id).first() is not None,
        "watched": Watched.query.filter_by(user_id=u.id, movie_id=id).first() is not None
    })


# ======================================================
# WATCHLIST / WATCHED
# ======================================================

@main.route("/watchlist/toggle", methods=["POST"])
def toggle_watchlist():
    u = current_user()
    if not u:
        return jsonify({"error": "Unauthorized"}), 401

    movie_id = request.json.get("movie_id")
    item = Watchlist.query.filter_by(user_id=u.id, movie_id=movie_id).first()

    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"status": "removed"})

    db.session.add(Watchlist(user_id=u.id, movie_id=movie_id))
    db.session.commit()
    return jsonify({"status": "added"})


@main.route("/watched/toggle", methods=["POST"])
def toggle_watched():
    u = current_user()
    if not u:
        return jsonify({"error": "Unauthorized"}), 401

    movie_id = request.json.get("movie_id")

    Watchlist.query.filter_by(user_id=u.id, movie_id=movie_id).delete()
    watched = Watched.query.filter_by(user_id=u.id, movie_id=movie_id).first()

    if watched:
        db.session.delete(watched)
        db.session.commit()
        return jsonify({"status": "removed"})

    db.session.add(Watched(user_id=u.id, movie_id=movie_id))
    db.session.commit()
    return jsonify({"status": "added"})


# ======================================================
# REVIEWS
# ======================================================

@main.route("/review", methods=["POST"])
def add_review():
    u = current_user()
    if not u:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    review = Review(
        user_id=u.id,
        movie_id=data["movie_id"],
        rating=data["rating"],
        comment=data.get("comment", "")
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review added"}), 201


@main.route("/movie/<int:id>/reviews")
def get_reviews(id):
    reviews = Review.query.filter_by(movie_id=id).all()
    return jsonify([{
        "id": r.id,
        "user_id": r.user_id,
        "username": r.user.username,
        "avatar": r.user.avatar,
        "rating": r.rating,
        "comment": r.comment
    } for r in reviews])


@main.route("/review/<int:id>", methods=["DELETE"])
def delete_review(id):
    u = current_user()
    r = Review.query.get_or_404(id)

    if not u or r.user_id != u.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(r)
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ======================================================
# PROFILE
# ======================================================

@main.route("/profile")
def profile():
    u = current_user()
    if not u:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "username": u.username,
        "email": u.email,
        "name": u.name,
        "age": u.age,
        "avatar": u.avatar
    })


@main.route("/profile/update", methods=["POST"])
def update_profile():
    u = current_user()
    data = request.json
    u.name = data.get("name", u.name)
    u.age = data.get("age", u.age)
    u.avatar = data.get("avatar", u.avatar)
    db.session.commit()
    return jsonify({"message": "Profile updated"})

@main.route("/profile/watchlist")
def profile_watchlist():
    u = current_user()
    if not u:
        return jsonify([])

    return jsonify([{
        "id": w.movie.tmdb_id,      # TMDB ID for MovieRow navigation
        "title": w.movie.title,
        "poster_path": w.movie.poster_path
    } for w in u.watchlist])

@main.route("/profile/reviews")
def profile_reviews():
    u = current_user()
    if not u:
        return jsonify([])

    return jsonify([{
        "movie_title": r.movie.title,
        "rating": r.rating,
        "comment": r.comment
    } for r in u.reviews])

@main.route("/profile/watched")
def profile_watched():
    u = current_user()
    if not u:
        return jsonify([])

    return jsonify([{
        "id": w.movie.tmdb_id,
        "tmdb_id": w.movie.tmdb_id,
        "title": w.movie.title,
        "poster_path": w.movie.poster_path
    } for w in u.watched])



# ======================================================
# SEARCH
# ======================================================

@main.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    movies_map = {}  # Deduplicate by TMDB ID

    # 1️⃣ Search movies by title
    movie_res = tmdb_get("/search/movie", {"query": q})
    for m in movie_res.get("results", []):
        movies_map[m["id"]] = {
            "tmdb_id": m["id"],
            "title": m["title"],
            "poster_path": m.get("poster_path")
        }

    # 2️⃣ Search people (cast & directors)
    person_res = tmdb_get("/search/person", {"query": q})

    for person in person_res.get("results", [])[:3]:  # Limit for performance
        person_id = person["id"]

        credits = tmdb_get(f"/person/{person_id}/movie_credits")

        # 🎭 Acting roles
        for m in credits.get("cast", []):
            movies_map.setdefault(m["id"], {
                "tmdb_id": m["id"],
                "title": m["title"],
                "poster_path": m.get("poster_path")
            })

        # 🎥 Director roles
        for m in credits.get("crew", []):
            if m.get("job") == "Director":
                movies_map.setdefault(m["id"], {
                    "tmdb_id": m["id"],
                    "title": m["title"],
                    "poster_path": m.get("poster_path")
                })

    # 3️⃣ Return top 15 unique movies
    return jsonify(list(movies_map.values())[:15])



# ======================================================
# RECOMMENDATIONS
# ======================================================

# -------------------------------------------------
# COLLABORATIVE RECOMMENDATION
# -------------------------------------------------
@main.route("/recommend/collaborative")
def recommend_collaborative_route():
    user = current_user()
    if not user:
        return jsonify([])

    internal_ids = recommend_collaborative(user.id, top_n=10)

    if not internal_ids:
        return jsonify([])

    movies = Movie.query.filter(Movie.id.in_(internal_ids)).all()

    return jsonify([
        {
            "id": m.tmdb_id,          # ✔ frontend always gets TMDB ID
            "title": m.title,
            "poster_path": m.poster_path
        }
        for m in movies
    ])


# -------------------------------------------------
# CONTENT-BASED RECOMMENDATION
# -------------------------------------------------
@main.route("/recommend/content/<int:tmdb_id>")
def recommend_content(tmdb_id):
    movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()
    if not movie:
        return jsonify([])

    # ML model uses INTERNAL DB ID
    internal_ids = recommend_similar_movies(movie.id, top_n=10)

    # -----------------------------
    # FALLBACK → TMDB similar
    # -----------------------------
    if not internal_ids:
        res = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}/similar",
            params={"api_key": TMDB_API_KEY}
        ).json()

        return jsonify([
            {
                "id": m["id"],
                "title": m.get("title", ""),
                "poster_path": m.get("poster_path", "")
            }
            for m in res.get("results", [])[:10]
        ])

    movies = Movie.query.filter(Movie.id.in_(internal_ids)).all()

    return jsonify([
        {
            "id": m.tmdb_id,
            "title": m.title,
            "poster_path": m.poster_path
        }
        for m in movies
    ])


# -------------------------------------------------
# CREW / DIRECTOR-BASED RECOMMENDATION
# -------------------------------------------------
@main.route("/recommend/crew/<int:tmdb_id>")
def recommend_crew(tmdb_id):
    seed = Movie.query.filter_by(tmdb_id=tmdb_id).first()
    if not seed:
        return jsonify([])

    # Pass internal ID to recommender
    recommended_internal_ids = recommend_by_crew(seed.id, top_n=10)

    movies = Movie.query.filter(Movie.id.in_(recommended_internal_ids)).all()

    return jsonify([
        {
            "id": m.tmdb_id,
            "title": m.title,
            "poster_path": m.poster_path
        }
        for m in movies
    ])



# -------------------------------------------------
# HYBRID RECOMMENDATION
# -------------------------------------------------
@main.route("/recommend/hybrid")
def recommend_hybrid():
    tmdb_id = request.args.get("movie_id", type=int)
    user = current_user()

    if not tmdb_id and not user:
        return jsonify([])

    movie = Movie.query.filter_by(tmdb_id=tmdb_id).first() if tmdb_id else None
    internal_id = movie.id if movie else None

    internal_ids = hybrid_recommendation(
        movie_id=internal_id,
        user_id=user.id if user else None,
        top_n=10
    )

    if not internal_ids:
        return jsonify([])

    movies = Movie.query.filter(Movie.id.in_(internal_ids)).all()

    return jsonify([
        {
            "id": m.tmdb_id,
            "title": m.title,
            "poster_path": m.poster_path
        }
        for m in movies
    ])


# -------------------------------------------------
# TOP-RATED (TMDB SEED + DB SAFE)
# -------------------------------------------------
@main.route("/recommend/top-rated")
def recommend_top_rated():
    user = current_user()

    watched_tmdb_ids = set()
    if user:
        watched_tmdb_ids = {w.movie.tmdb_id for w in user.watched}

    res = requests.get(
        f"{TMDB_BASE}/movie/top_rated",
        params={"api_key": TMDB_API_KEY}
    ).json()

    results = []

    for m in res.get("results", []):
        tmdb_id = m.get("id")

        if tmdb_id in watched_tmdb_ids:
            continue

        movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()
        if not movie:
            movie = Movie(
                tmdb_id=tmdb_id,
                title=m.get("title", ""),
                poster_path=m.get("poster_path", ""),
                popularity=m.get("popularity", 0)
            )
            db.session.add(movie)

        results.append(movie)

        if len(results) >= 20:
            break

    db.session.commit()

    return jsonify([
        {
            "id": m.tmdb_id,
            "title": m.title,
            "poster_path": m.poster_path
        }
        for m in results
    ])
