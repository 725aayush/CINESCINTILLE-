import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # SQLite database
    SQLALCHEMY_DATABASE_URI = "sqlite:///cinema.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
