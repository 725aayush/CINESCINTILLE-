from backend.app import create_app
from database.db import db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database recreated with avatar column")
