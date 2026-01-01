from flask import Blueprint, jsonify, session
from database.models import User

auth = Blueprint("auth", __name__)

@auth.route("/me")
def get_me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(None), 200

    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })
