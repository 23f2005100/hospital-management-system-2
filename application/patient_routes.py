from flask import request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.database import db
from application.models import Patient, User, Doctor, Department, Appointment, Availability
from datetime import date, timedelta
from application.cache_utils import get_cached, set_cached, delete_cached

def get_patient():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != "patient":
        return None, (jsonify({"error": "Patient access required"}))
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return None, (jsonify({"error": "Patient profile not found"}))
    return patient, None


@app.route("/api/patient/dashboard", methods=["GET"])
@jwt_required()
def patient_dashboard():
    patient, err = get_patient()
    if err: return err

    departments = Department.query.all()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status     == "Booked",
        Appointment.date       >= date.today()
    ).order_by(Appointment.date.asc()).all()

    return jsonify({
        "patient":      patient.to_dict(),
        "departments":  [d.to_dict() for d in departments],
        "upcoming":     [a.to_dict() for a in upcoming],
    })

@app.route("/api/patient/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    patient, err = get_patient()
    if err: return err

    user = User.query.get(patient.user_id)
    data = request.get_json()

    # Patient model fields
    patient.name    = data.get("name",    patient.name)
    patient.contact = data.get("contact", patient.contact)
    patient.gender  = data.get("gender",  patient.gender)
    patient.age     = data.get("age",     patient.age)

    # Email update
    new_email = data.get("email")
    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({"error": "Email already in use"})
        user.email = new_email

    # Password update - no old password needed
    new_password = data.get("password")
    if new_password:
        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(new_password)

    db.session.commit()
    return jsonify(patient.to_dict())

@app.route("/api/patient/departments/<int:dept_id>", methods=["GET"])
@jwt_required()
def get_department_doctors(dept_id):
    patient, err = get_patient()
    if err: return err

    cache_key = f"dept:{dept_id}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)

    dept = Department.query.get(dept_id)
    doctors = Doctor.query.join(User).filter(
        Doctor.department_id == dept_id
    ).all()

    data = {"department": dept.to_dict(), "doctors": [d.to_dict() for d in doctors]}
    set_cached(cache_key, data, ttl=300)  # 5 min
    return jsonify(data)

@app.route("/api/patient/doctors/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_doctor_profile(doctor_id):
    patient, err = get_patient()
    if err: return err
    
    today = date.today()
    next_week = today + timedelta(days=7)

    doctor = Doctor.query.get(doctor_id)
    if doctor.user.is_blacklisted:              # 
        return jsonify({"error": "Doctor not available"})
    
    cache_key = f"doctor:{doctor_id}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    slots = Availability.query.filter(
        Availability.doctor_id == doctor_id,
        Availability.is_available == True,
        Availability.date >= date.today(),
        Availability.date <= next_week
    ).order_by(Availability.date.asc()).all()

    data = {"doctor": doctor.to_dict(), "availability": [s.to_dict() for s in slots]}
    set_cached(cache_key, data, ttl=180)  # 3 min
    return jsonify(data)


@app.route("/api/patient/book/<int:slot_id>", methods=["POST"])
@jwt_required()
def book_appointment(slot_id):
    patient, err = get_patient()
    if err: return err

    slot = Availability.query.get(slot_id)

    if not slot.is_available:
        return jsonify({"error": "Slot not available"})
    
    existing = Appointment.query.filter_by(
    doctor_id=slot.doctor_id,
    date=slot.date,
    time=slot.slot,
    status="Booked"
    ).first()
    if existing:
        return jsonify({"error": "Slot already booked"})

    appointment = Appointment(
        doctor_id  = slot.doctor_id,
        patient_id = patient.id,
        date       = slot.date,
        time = slot.slot,
        status     = "Booked"
    )
    db.session.add(appointment)
    slot.is_available = False
    db.session.commit()
    delete_cached(f"doctor:{slot.doctor_id}")
    return jsonify({"message": "Appointment booked"})

@app.route("/api/patient/appointments/<int:app_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_appointment(app_id):
    patient, err = get_patient()
    if err: return err

    appointment = Appointment.query.get(app_id)
    if appointment.patient_id != patient.id:
        return jsonify({"error": "Unauthorized"})
    if appointment.status != "Booked":
        return jsonify({"error": "Only booked appointments can be cancelled"})

    appointment.status       = "Cancelled"
    appointment.cancelled_by = "patient"   # NEW

    # restore slot
    slot = Availability.query.filter_by(
        doctor_id = appointment.doctor_id,
        date      = appointment.date,
        slot      = appointment.time
    ).first()
    if slot:
        slot.is_available = True

    db.session.commit()
    delete_cached(f"doctor:{appointment.doctor_id}")
    return jsonify({"message": "Appointment cancelled"})

@app.route("/api/patient/search", methods=["GET"])
@jwt_required()
def patient_search():
    patient, err = get_patient()
    if err: return err

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"doctors": []})

    doctors = Doctor.query.join(Department).join(User).filter(
        User.is_blacklisted == False,
        db.or_(
            Doctor.fullname.ilike(f"%{q}%"),
            Doctor.specialization.ilike(f"%{q}%"),
            Department.name.ilike(f"%{q}%")
        )
    ).all()

    return jsonify({"doctors": [d.to_dict() for d in doctors]})

@app.route("/api/patient/history", methods=["GET"])
@jwt_required()
def patient_history():
    patient, err = get_patient()
    if err: return err

    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status.in_(["Completed", "Cancelled"])
    ).order_by(Appointment.date.desc()).all()

    return jsonify([a.to_dict() for a in appointments])

@app.route("/api/patient/export", methods=["POST"])
@jwt_required()
def export_history():
    patient, err = get_patient()
    if err: return err

    from application.tasks import export_patient_csv
    export_patient_csv.delay(patient.id)
    return jsonify({"message": "Export started! You will be notified when ready."})