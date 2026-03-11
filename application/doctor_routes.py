from flask import request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.database import db
from application.models import Doctor, Patient, Appointment, Treatment, Availability, User
from datetime import date, datetime, timedelta
import json
from application.cache_utils import get_cached, set_cached, delete_cached

def get_doctor():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != "doctor":
        return None, jsonify({"error": "Doctor access required"})
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return None, (jsonify({"error": "Doctor profile not found"}))
    return doctor, None

@app.route("/api/doctor/dashboard", methods=["GET"])
@jwt_required()
def doctor_dashboard():
    doctor, err = get_doctor()
    if err: return err

    upcoming = Appointment.query.filter_by(
        doctor_id=doctor.id, status="Booked"
    ).all()
    
    assigned_patients = (
    Patient.query
    .join(Appointment, Appointment.patient_id == Patient.id)
    .filter(Appointment.doctor_id == doctor.id)
    .distinct().all())

    past = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status.in_(["Completed", "Cancelled"])
    ).order_by(Appointment.date.desc()).all()

    return jsonify({
        "doctor":   doctor.to_dict(),
        "upcoming": [a.to_dict() for a in upcoming],
        "assigned": [a.to_dict() for a in assigned_patients],
        "past":     [a.to_dict() for a in past]
    })


@app.route("/api/doctor/appointments/<int:app_id>/cancel", methods=["POST"])
@jwt_required()
def doctor_cancel_appointment(app_id):
    doctor, err = get_doctor()
    if err: return err

    appointment = Appointment.query.get(app_id)
    if appointment.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"})

    appointment.status       = "Cancelled"
    appointment.cancelled_by = "doctor"    # NEW

    # restore slot
    slot = Availability.query.filter_by(
        doctor_id = appointment.doctor_id,
        date      = appointment.date,
        slot      = appointment.time
    ).first()
    if slot:
        slot.is_available = True

    db.session.commit()
    return jsonify({"message": "Appointment cancelled"})

@app.route("/api/doctor/appointments/<int:app_id>/treatment", methods=["POST"])
@jwt_required()
def update_treatment(app_id):
    doctor, err = get_doctor()
    if err: return err

    appointment = Appointment.query.get(app_id)
    if appointment.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"})

    data      = request.get_json()
    treatment = Treatment.query.filter_by(appointment_id=app_id).first()

    if treatment:
        # update existing
        treatment.visit_type   = data.get("visit_type",   treatment.visit_type)
        treatment.test_done    = data.get("test_done",    treatment.test_done)
        treatment.diagnosis    = data.get("diagnosis",    treatment.diagnosis)
        treatment.prescription = data.get("prescription", treatment.prescription)
        treatment.medicines    = data.get("medicines",    treatment.medicines)
        treatment.next_visit   = data.get("next_visit",   treatment.next_visit)
        treatment.notes        = data.get("notes",        treatment.notes)
    else:
        # create new
        treatment = Treatment(
            appointment_id = app_id,
            visit_type     = data.get("visit_type"),
            test_done      = data.get("test_done"),
            diagnosis      = data.get("diagnosis"),
            prescription   = data.get("prescription"),
            medicines      = data.get("medicines"),
            next_visit     = data.get("next_visit"),
            notes          = data.get("notes"),
        )
        db.session.add(treatment)

    appointment.status = "Completed"
    db.session.commit()
    return jsonify({"message": "Treatment saved"}), 200

@app.route("/api/doctor/patient/<int:patient_id>/history", methods=["GET"])
@jwt_required()
def doctor_patient_history(patient_id):
    doctor, err = get_doctor()
    if err: return err

    patient      = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).order_by(Appointment.date.desc()).all()

    return jsonify({
        "patient":      patient.to_dict(),
        "appointments": [a.to_dict() for a in appointments]
    })

from datetime import date, timedelta

@app.route('/api/doctor/availability', methods=['GET'])
@jwt_required()
def get_availability():
    doctor, err = get_doctor()
    if err: return err

    cache_key = f"availability:doctor:{doctor.id}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached), 200

    today = date.today()
    next_week = today + timedelta(days=7)

    slots = Availability.query.filter_by(doctor_id=doctor.id)\
            .filter(Availability.date >= today)\
            .filter(Availability.date <= next_week)\
            .all()
    result = {"slots": [s.to_dict() for s in slots]}
    set_cached(cache_key, result, ttl=120)  # 'result' defined just above as earlier data was not defined nd thus was giving results. return jsonify({"result": "s.to_dict() for s in slots"})
    return jsonify(result)


@app.route('/api/doctor/availability', methods=['POST'])
@jwt_required()
def add_availability():
    doctor, err = get_doctor()
    if err: return err

    data = request.get_json()
    slot = Availability(
    doctor_id = doctor.id,
    date      = datetime.strptime(data['date'], '%Y-%m-%d').date(),
    slot      = data['slot'])
    db.session.add(slot)
    db.session.commit()
    delete_cached(f"availability:doctor:{doctor.id}")
    delete_cached(f"doctor:{doctor.id}") 
    return jsonify({"message": "Slot added"})


@app.route("/api/doctor/availability/<int:slot_id>", methods=["DELETE"])
@jwt_required()
def delete_availability(slot_id):
    doctor, err = get_doctor()
    if err: return err

    slot = Availability.query.get_or_404(slot_id)
    if slot.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(slot)
    db.session.commit()
    delete_cached(f"availability:doctor:{doctor.id}")
    delete_cached(f"doctor:{doctor.id}")   # ← add this
    return jsonify({"message": "Slot removed"}), 200