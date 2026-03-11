from flask import request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from application.database import db
from application.models import User, Doctor, Patient, Appointment, Department, Availability
from application.cache_utils import get_cached, set_cached, delete_cached
from datetime import date
def admin_only():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != "admin":
        return jsonify({"error": "Admin access required"})
    return None


@app.route("/api/admin/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    err = admin_only()
    if err: return err
    
    doctors  = Doctor.query.all()
    patients = Patient.query.all()
    upcoming = Appointment.query.filter_by(status="Booked").all()
    previous = Appointment.query.filter_by(status="Completed").all()
    return jsonify({"doctors": [d.to_dict() for d in doctors], "patients": [p.to_dict() for p in patients], 
                    "upcoming": [ua.to_dict() for ua in upcoming], "previous": [pa.to_dict() for pa in previous]
        
    })


@app.route("/api/admin/doctors", methods=["GET"])
@jwt_required()
def get_doctors():
    err = admin_only()
    if err: return err
    doctors = Doctor.query.all()
    return jsonify({"result": [d.to_dict() for d in doctors]})


@app.route("/api/admin/doctors", methods=["POST"])
@jwt_required()
def add_doctor():
    err = admin_only()
    if err: return err

    data = request.get_json()
    required = ["fullname", "email", "password", "qualification", "experience", "department_id"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "All fields required"})
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"})

    user = User(email=data["email"],
                password=generate_password_hash(data["password"]),
                role="doctor")
    db.session.add(user)
    db.session.commit()

    doctor = Doctor(
        user_id=user.id,
        fullname=data["fullname"],
        qualification=data["qualification"],
        specialization=data.get("specialization", ""),
        experience=data["experience"],
        description=data.get("description", ""),
        contact=data.get("contact", ""),
        department_id=data["department_id"]
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({"result" : [doctor.to_dict()]})


@app.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
@jwt_required()
def edit_doctor(doctor_id):                #change this code at last
    err = admin_only()
    if err: return err

    doctor = Doctor.query.get(doctor_id)
    data   = request.get_json()

    doctor.fullname      = data.get("fullname",      doctor.fullname)
    doctor.specialization = data.get("specialization", doctor.specialization)
    doctor.qualification = data.get("qualification", doctor.qualification)
    doctor.experience    = data.get("experience",    doctor.experience)
    doctor.description   = data.get("description",   doctor.description)
    doctor.contact       = data.get("contact",       doctor.contact)
    doctor.department_id = data.get("department_id", doctor.department_id)
    db.session.commit()
    return jsonify(doctor.to_dict())

@app.route('/api/admin/blacklist/<string:role>/<int:id>', methods=['POST'])
@jwt_required()
def user_blacklist(role, id):
    err = admin_only()
    if err: return err

    if role == 'doctor':
        doctor = Doctor.query.get(id)
        user = User.query.get(doctor.user_id)
        delete_cached(f"dept:{doctor.department_id}")   
        delete_cached(f"doctor:{doctor.id}")            

        # cancel future booked appointments
        future_appointments = Appointment.query.filter_by(
            doctor_id=doctor.id, status="Booked"
        ).all()
        for appt in future_appointments:
            appt.status       = "Cancelled"
            appt.cancelled_by = "admin"
            slot = Availability.query.filter_by(
                doctor_id=doctor.id,
                date=appt.date,
                slot=appt.time
            ).first()
            if slot:
                slot.is_available = True
        
                # mark ALL future slots as unavailable  ← ADD THIS
        future_slots = Availability.query.filter(
            Availability.doctor_id == doctor.id,
            Availability.date >= date.today()
        ).all()
        for slot in future_slots:
            slot.is_available = False

    elif role == 'patient':
        patient = Patient.query.get(id)
        user = User.query.get(patient.user_id)
    else:
        return jsonify({"error": "Invalid role"})

    user.is_blacklisted = True
    db.session.commit()
    return jsonify({"message": "User blacklisted"})


@app.route('/api/admin/unblacklist/<string:role>/<int:id>', methods=['POST'])
@jwt_required()
def user_unblacklist(role, id):
    err = admin_only()
    if err: return err

    if role == 'doctor':
        doctor = Doctor.query.get(id)
        user = User.query.get(doctor.user_id)

        # restore future slots
        future_slots = Availability.query.filter(
            Availability.doctor_id == doctor.id,
            Availability.date >= date.today()
        ).all()
        for slot in future_slots:
            slot.is_available = True

        delete_cached(f"dept:{doctor.department_id}")
        delete_cached(f"doctor:{doctor.id}")

    elif role == 'patient':
        patient = Patient.query.get(id)
        user = User.query.get(patient.user_id)
    else:
        return jsonify({"error": "Invalid role"})

    user.is_blacklisted = False
    db.session.commit()
    return jsonify({"message": "User unblacklisted"})

@app.route("/api/admin/dashboard/delete/<string:role>/<int:id>", methods = ["DELETE"])
@jwt_required()
def user_delete(role, id):
    err = admin_only()
    if err : return err

    if role == "doctor":
        doctor = Doctor.query.get(id)
        user = User.query.get(doctor.user_id)
        Appointment.query.filter_by(doctor_id=doctor.id).delete()
        Availability.query.filter_by(doctor_id=doctor.id).delete()
        db.session.delete(doctor)
        db.session.delete(user)

    elif role == "patient":
        patient = Patient.query.get(id)
        user = User.query.get(patient.user_id)
        Appointment.query.filter_by(patient_id=patient.id).delete()
        db.session.delete(patient)
        db.session.delete(user)
    else:
        return jsonify({"message" : "Role doesn't exist"})

    db.session.commit()
    return jsonify({"message" : "User deleted from system."})

@app.route("/api/admin/patients", methods=["GET"])
@jwt_required()
def get_patients():
    err = admin_only()
    if err: return err

    patients = Patient.query.all()
    return jsonify({"result": [p.to_dict() for p in patients]})


@app.route("/api/admin/patients/<int:patient_id>", methods=["PUT"])
@jwt_required()
def edit_patient(patient_id):
    err = admin_only()
    if err: return err

    patient = Patient.query.get(patient_id)
    data    = request.get_json()
    patient.name    = data.get("name",    patient.name)
    patient.contact = data.get("contact", patient.contact)
    patient.gender  = data.get("gender",  patient.gender)
    patient.age     = data.get("age",     patient.age)
    db.session.commit()
    return jsonify(patient.to_dict())   #change this line.


@app.route("/api/admin/appointments", methods=["GET"])
@jwt_required()
def get_all_appointments():
    err = admin_only()
    if err: return err

    status = request.args.get("status")  # optional filter
    query  = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments])




@app.route("/api/admin/departments", methods=["GET"])
@jwt_required()
def admin_get_departments():
    err = admin_only()
    if err: return err

    depts  = Department.query.all()
    result = [d.to_dict() for d in depts]
    return jsonify(result)

@app.route("/api/admin/search", methods=["GET"])
@jwt_required()
def admin_search():
    err = admin_only()
    if err: return err

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"doctors": [], "patients": []})

    doctors = Doctor.query.join(Department).filter(
        db.or_(
            Doctor.fullname.ilike(f"%{q}%"),
            Department.name.ilike(f"%{q}%"),
            Doctor.specialization.ilike(f"%{q}%")
        )
    ).all()

    patients = Patient.query.filter(
        db.or_(
            Patient.name.ilike(f"%{q}%"),
            Patient.contact.ilike(f"%{q}%")
        )
    ).all()

    return jsonify({
        "doctors":  [d.to_dict() for d in doctors],
        "patients": [p.to_dict() for p in patients]
    })

@app.route("/api/admin/departments", methods=["POST"])
@jwt_required()
def add_department():
    err = admin_only()
    if err: return err

    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"})
    if Department.query.filter_by(name=name).first():
        return jsonify({"error": "Department already exists"})

    dept = Department(name=name, description=data.get("description", ""))
    db.session.add(dept)
    db.session.commit()
    return jsonify(dept.to_dict())

@app.route("/api/admin/trigger-reminders", methods=["POST"])
@jwt_required()
def trigger_reminders():
    err = admin_only()
    if err: return err

    from application.tasks import send_daily_reminders
    send_daily_reminders.delay()
    return jsonify({"message": "Daily reminders job triggered"})


@app.route("/api/admin/trigger-report", methods=["POST"])
@jwt_required()
def trigger_report():
    err = admin_only()
    if err: return err

    from application.tasks import generate_monthly_report
    generate_monthly_report.delay()
    return jsonify({"message": "Monthly report job triggered"})