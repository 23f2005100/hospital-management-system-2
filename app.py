from flask import Flask
from application.database import db
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from application.celery_utils import make_celery          # NEW
from celery.schedules import crontab          # NEW

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-for-hospital-management-system'

db.init_app(app)
JWTManager(app)
CORS(app)

app.app_context().push()

celery = make_celery(app)                     # NEW
celery.conf.update(include=['application.tasks'])

celery.conf.beat_schedule = {                 # NEW
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0)
    },
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0)
    }
}

from application import auth_routes
from application import admin_routes
from application import doctor_routes
from application import patient_routes

if __name__ == '__main__':
    with app.app_context():
        from application.models import User, Department
        db.create_all()

        if not User.query.filter_by(role='admin').first():
            admin = User(
                email='admin@hospital.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin created')

        if Department.query.count() == 0:
            for name, desc in [
                ('Cardiology',  'Heart and cardiovascular system'),
                ('Oncology',    'Cancer diagnosis and treatment'),
                ('General',     'General medicine and primary care'),
                ('Neurology',   'Brain and nervous system'),
                ('Orthopedics', 'Bone and muscle specialists'),
            ]:
                db.session.add(Department(name=name, description=desc))
            db.session.commit()
            print('✅ Departments seeded')

    app.run(debug=True)