from app import celery
from application.models import Appointment, Patient, User
from application.database import db
from datetime import date, timedelta
import csv
import os

from application.mail_utils import send_email
from application.mail_utils import send_email, send_email_with_attachment

@celery.task
def send_daily_reminders():
    today = date.today()
    appointments = Appointment.query.filter_by(date=today, status="Booked").all()

    for appt in appointments:
        patient = Patient.query.get(appt.patient_id)
        user    = User.query.get(patient.user_id)
        html = f"""
        <h2>Hospital Reminder</h2>
        <p>Hi {patient.name}, you have an appointment today at <b>{appt.time}</b>.</p>
        <p>Please visit the hospital on time.</p>
        """
        send_email(user.email, "Appointment Reminder", html)

    return f"Sent {len(appointments)} reminders"


@celery.task
def generate_monthly_report():
    from sqlalchemy import extract
    from application.models import Doctor

    today = date.today()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    month = last_month.month
    year  = last_month.year
    # month = today.month
    # year = today.year
    
    doctors = Doctor.query.all()
    for doctor in doctors:
        user = User.query.get(doctor.user_id)
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status    == "Completed",
            extract('month', Appointment.date) == month,
            extract('year',  Appointment.date) == year
        ).all()

        html = f"<h2>Monthly Report — Dr. {doctor.fullname} ({year}-{month:02d})</h2>"
        html += f"<p>Total Completed Appointments: {len(appointments)}</p><ul>"
        for appt in appointments:
            patient   = Patient.query.get(appt.patient_id)
            t = appt.treatment
            html += f"""
            <li style="margin-bottom:10px;">
                <strong>{patient.name}</strong> on {appt.date}<br/>
                Visit Type: {t.visit_type   if t else 'N/A'}<br/>
                Tests Done: {t.test_done    if t else 'N/A'}<br/>
                Diagnosis:  {t.diagnosis    if t else 'N/A'}<br/>
                Rx:         {t.prescription if t else 'N/A'}<br/>
                Medicines:  {t.medicines    if t else 'N/A'}<br/>
                Notes:      {t.notes        if t else 'N/A'}<br/>
                Next Visit: {t.next_visit   if t else 'N/A'}
            </li>"""

        send_email(user.email, f"Monthly Report - {year}-{month:02d}", html)

    return "Monthly reports sent"


@celery.task
def export_patient_csv(patient_id):
    import csv, os
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
        writer.writerow([
            "User ID", "Patient Name", "Doctor", "Date",
            "Visit Type", "Tests Done", "Diagnosis",
            "Prescription", "Medicines", "Notes", "Next Visit"
        ])
        for appt in appointments:
            doctor    = Doctor.query.get(appt.doctor_id)
            t         = appt.treatment
            writer.writerow([
                user.id, patient.name, doctor.fullname, appt.date,
                t.visit_type   if t else "N/A",
                t.test_done    if t else "N/A",
                t.diagnosis    if t else "N/A",
                t.prescription if t else "N/A",
                t.medicines    if t else "N/A",
                t.notes        if t else "N/A",
                t.next_visit   if t else "N/A",
            ])

    send_email_with_attachment(
        to        = user.email,
        subject   = "Your CSV Export is Ready",
        html_body = f"<h2>Export Ready</h2><p>Hi {patient.name}, your treatment history is attached.</p>",
        filepath  = filepath,
        filename  = filename
    )
    return f"Export done + email sent: {filepath}"