from app import celery
from application.models import Appointment, Patient, User
from application.database import db
from datetime import date, timedelta
import csv
import os

@celery.task
def send_daily_reminders():
    today = date.today()
    appointments = Appointment.query.filter_by(date=today, status="Booked"
    ).all()

    for appt in appointments:
        patient = Patient.query.get(appt.patient_id)
        user    = User.query.get(patient.user_id)
        # In real app you'd send email here
        # For now just print
        print(f"[REMINDER] {user.email} — appointment today at {appt.time}")

    return f"Sent {len(appointments)} reminders"

@celery.task
def generate_monthly_report():
    from sqlalchemy import extract
    from application.models import Doctor

    today = date.today()
    # first day of current month → go back 1 day → gives last month
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    month = last_month.month
    year  = last_month.year

    doctors = Doctor.query.all()

    for doctor in doctors:
        user = User.query.get(doctor.user_id)

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "Completed",
            extract('month', Appointment.date) == month,
            extract('year',  Appointment.date) == year
        ).all()

        print(f"\n[MONTHLY REPORT] Doctor: {doctor.fullname} | {year}-{month:02d}")
        print(f"  Total Completed: {len(appointments)}")
        for appt in appointments:
            patient = Patient.query.get(appt.patient_id)
            treatment = appt.treatment  # backref from Treatment model
            diagnosis = treatment.diagnosis if treatment else "N/A"
            print(f"  - {patient.name} on {appt.date} | Diagnosis: {diagnosis}")

    return "Monthly reports generated"

@celery.task
def export_patient_csv(patient_id):
    from application.models import Patient, Appointment, Doctor, User

    patient = Patient.query.get(patient_id)
    user    = User.query.get(patient.user_id)

    appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.status.in_(["Completed", "Cancelled"])
    ).all()

    filename = f"patient_{patient_id}_export.csv"
    filepath = os.path.join("exports", filename)
    os.makedirs("exports", exist_ok=True)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Patient Name", "Doctor", "Date", "Diagnosis", "Treatment", "Next Visit"])

        for appt in appointments:
            doctor    = Doctor.query.get(appt.doctor_id)
            treatment = appt.treatment
            writer.writerow([
                user.id,
                patient.name,
                doctor.fullname,
                appt.date,
                treatment.diagnosis   if treatment else "N/A",
                treatment.prescription if treatment else "N/A",
                treatment.next_visit  if treatment else "N/A",
            ])

    print(f"[CSV EXPORT] Export ready for {user.email} → {filepath}")
    return f"Export done: {filepath}"