from database.db import db
from werkzeug.security import generate_password_hash, check_password_hash


# ======================================================
# USER
# ======================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    avatar = db.Column(db.String(255), default="default.png")

    # Relationships
    watchlist = db.relationship("Watchlist", back_populates="user", cascade="all, delete")
    watched = db.relationship("Watched", back_populates="user", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ======================================================
# MOVIE
# ======================================================

class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)

    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.Text)
    genres = db.Column(db.String(255))
    release_date = db.Column(db.String(20))
    runtime = db.Column(db.Integer)
    language = db.Column(db.String(50))
    poster_path = db.Column(db.String(255))
    popularity = db.Column(db.Float)

    director = db.Column(db.String(255))
    cast = db.Column(db.Text)

    reviews = db.relationship("Review", back_populates="movie", cascade="all, delete")


# ======================================================
# REVIEW
# ======================================================

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    user = db.relationship("User", back_populates="reviews")
    movie = db.relationship("Movie", back_populates="reviews")


# ======================================================
# WATCHLIST
# ======================================================

class Watchlist(db.Model):
    __tablename__ = "watchlist"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)

    user = db.relationship("User", back_populates="watchlist")
    movie = db.relationship("Movie")


# ======================================================
# WATCHED
# ======================================================

class Watched(db.Model):
    __tablename__ = "watched"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)

    user = db.relationship("User", back_populates="watched")
    movie = db.relationship("Movie")
