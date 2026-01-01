from flask import Flask
from flask_cors import CORS
from flask_session import Session
from database.db import db
from backend.routes import main
import os
import sys

# Ensure root path is available
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)


def create_app():
    app = Flask(__name__)

    # -----------------------
    # BASIC CONFIG
    # -----------------------
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    # ⚠️ TEMP: SQLite (works on Render free tier)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///cinema.db"
    ).replace("postgres://", "postgresql://")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -----------------------
    # SESSION CONFIG (CRITICAL)
    # -----------------------
    app.config.update(
        SESSION_TYPE="filesystem",
        SESSION_FILE_DIR="/tmp/flask_session",
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        SESSION_COOKIE_HTTPONLY=True,

        # 🔥 THESE TWO FIX YOUR ISSUE
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True,
    )

    Session(app)
    db.init_app(app)

    # Auto-create tables (OK for now)
    with app.app_context():
        db.create_all()

    # -----------------------
    # CORS CONFIG (CRITICAL)
    # -----------------------
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:3000",
                    "https://cinescintille.vercel.app"
                ]
            }
        }
    )

    # -----------------------
    # ROUTES
    # -----------------------
    app.register_blueprint(main)

    return app


# Gunicorn entry point
app = create_app()
