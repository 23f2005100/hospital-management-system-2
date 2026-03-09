from flask import request, jsonify, current_app as app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import User, Patient, Doctor
from application.database import db


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"})

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"})
    if not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid password"})
    if user.is_blacklisted:
        return jsonify({"error": "Account is blacklisted."})

    # get profile_id so Vue knows which dashboard data to fetch
    profile_id = None
    name       = None
    if user.role == "patient":
        p = Patient.query.filter_by(user_id=user.id).first()
        profile_id = p.id if p else None
        name = p.name if p else None
    elif user.role == "doctor":
        d          = Doctor.query.filter_by(user_id=user.id).first()
        profile_id = d.id       if d else None
        name       = d.fullname if d else None
    elif user.role == "admin":
        name = "Admin"

    token = create_access_token(identity=str(user.id)) 
    return jsonify({"token": token, "role": user.role,
                    "user_id": user.id, "profile_id":profile_id, "name":name})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name     = data.get("name")
    email    = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields required"})
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"})

    user = User(email=email, password=generate_password_hash(password), role="patient")
    db.session.add(user)
    db.session.commit()

    patient = Patient(name=name, user_id=user.id)
    db.session.add(patient)
    db.session.commit()

    token = create_access_token(identity=str(user.id))  
    return jsonify({"token": token, "role": "patient",
                    "user_id": user.id})