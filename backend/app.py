from flask import Flask
from flask_cors import CORS
from flask_session import Session
from database.db import db
from backend.routes import main
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cinema.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # SESSION
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session")
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    Session(app)
    db.init_app(app)

    # ✅ CORRECT CORS (THIS FIXES /me)
    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:3000"]
    )

    # ✅ NO /api PREFIX
    app.register_blueprint(main)

    return app
