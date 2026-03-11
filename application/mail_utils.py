import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app

def send_email(to, subject, html_body):
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = username
    msg["To"]      = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, to, msg.as_string())


def send_email_with_attachment(to, subject, html_body, filepath, filename):
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"]    = username
    msg["To"]      = to
    msg.attach(MIMEText(html_body, "html"))

    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, to, msg.as_string())