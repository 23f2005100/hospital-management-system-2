# application/routes/auth_routes.py

from flask import request, jsonify, current_app as app
from flask_jwt_extended import create_access_token
from application.models import User, Patient
from application.database import db


# =========================
# LOGIN
# =========================

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.password != password:
        return jsonify({"error": "Invalid password"}), 401

    access_token = create_access_token(
        identity={
            "id": user.id,
            "role": user.role
        }
    )

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "role": user.role,
        "user_id": user.id
    }), 200


# =========================
# REGISTER (Patient only)
# =========================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    user = User(
        email=email,
        password=password,
        role="patient"
    )

    db.session.add(user)
    db.session.commit()

    patient = Patient(
        name=name,
        user_id=user.id
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Registration successful"
    }), 201