from flask import Flask
from flask_cors import CORS
from flask_session import Session
from database.db import db
from backend.routes import main
import os
import sys

# -------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def create_app():
    app = Flask(__name__)

    # -------------------------------------------------
    # BASIC CONFIG
    # -------------------------------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # Database (Postgres on Render, SQLite fallback locally)
    database_url = os.getenv("DATABASE_URL", "sqlite:///cinema.db")

    # Render uses deprecated postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------------------------------------------------
    # SESSION CONFIG (REQUIRED FOR LOGIN TO WORK)
    # -------------------------------------------------
    app.config.update(
        SESSION_TYPE="filesystem",
        SESSION_FILE_DIR="/tmp/flask_session",
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        SESSION_COOKIE_HTTPONLY=True,

        # REQUIRED for Vercel → Render cookies
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True,
    )

    Session(app)

    # -------------------------------------------------
    # DATABASE INIT (SAFE)
    # -------------------------------------------------
    db.init_app(app)

    # Auto-create tables (acceptable on free tier)
    with app.app_context():
        db.create_all()

    # -------------------------------------------------
    # CORS CONFIG (CRITICAL)
    # -------------------------------------------------
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:3000",
                    "https://cinescintille.vercel.app",
                ]
            }
        },
    )

    # -------------------------------------------------
    # ROUTES
    # -------------------------------------------------
    app.register_blueprint(main)

    if os.getenv("RENDER") == "true":
        with app.app_context():
         db.create_all()

    return app


# -------------------------------------------------
# Gunicorn entry point
# -------------------------------------------------
app = create_app()
