from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.models import *
from application.database import db
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__)

def admin_required():
    identity = get_jwt_identity()
    if identity["role"] != "admin":
        return False
    return True

@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():

    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()

    upcoming_appointments = Appointment.query.filter(
        Appointment.status == "Booked",
        Appointment.date >= datetime.today().date()
    ).count()

    return jsonify({
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_appointments
    })

@admin_bp.route("/add-doctor", methods=["POST"])
@jwt_required()
def add_doctor():

    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    fullname = data.get("fullname")
    qualification = data.get("qualification")
    experience = data.get("experience")
    description = data.get("description")
    contact = data.get("contact")
    department_id = data.get("department_id")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(email=email, password=password, role="doctor")
    db.session.add(user)
    db.session.commit()

    doctor = Doctor(
        user_id=user.id,
        fullname=fullname,
        qualification=qualification,
        experience=experience,
        description=description,
        contact=contact,
        department_id=department_id
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({"message": "Doctor added successfully"})

@admin_bp.route("/delete-doctor/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
def delete_doctor(doctor_id):

    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    user = User.query.get(doctor.user_id)

    db.session.delete(doctor)
    if user:
        db.session.delete(user)

    db.session.commit()

    return jsonify({"message": "Doctor deleted"})

@admin_bp.route("/blacklist", methods=["POST"])
@jwt_required()
def blacklist_user():

    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    user_id = data.get("user_id")
    role = data.get("role")

    entry = Blacklist(user_id=user_id, user_role=role)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "User blacklisted"})

@admin_bp.route("/search", methods=["GET"])
@jwt_required()
def search():

    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    query = request.args.get("q")

    doctors = Doctor.query.filter(
        Doctor.fullname.ilike(f"%{query}%")
    ).all()

    patients = Patient.query.filter(
        Patient.name.ilike(f"%{query}%")
    ).all()

    return jsonify({
        "doctors": [
            {"id": d.id, "name": d.fullname}
            for d in doctors
        ],
        "patients": [
            {"id": p.id, "name": p.name}
            for p in patients
        ]
    })
