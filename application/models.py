from .database import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'user'
    id             = db.Column(db.Integer, primary_key=True)
    email          = db.Column(db.String(100), unique=True, nullable=False)
    password       = db.Column(db.String(200), nullable=False)   # hashed
    role           = db.Column(db.String(20),  nullable=False)   # admin | doctor | patient
    is_blacklisted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id':             self.id,
            'email':          self.email,
            'role':           self.role,
            'is_blacklisted': self.is_blacklisted,
        }

class Department(db.Model):
    __tablename__ = 'department'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    doctors     = db.relationship('Doctor', backref='department', lazy=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'name':         self.name,
            'description':  self.description,
            'doctor_count': len(self.doctors),
        }

class Doctor(db.Model):
    __tablename__ = 'doctor'
    user = db.relationship('User', backref='doctor')
    id            = db.Column(db.Integer, primary_key=True)
    fullname      = db.Column(db.String(100), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    specialization = db.Column(db.String(100))
    qualification = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    contact       = db.Column(db.String(20))
    experience    = db.Column(db.String(100), nullable=False)
    appointments  = db.relationship('Appointment', backref='doctor', lazy=True)
    availability  = db.relationship('Availability', backref='doctor', lazy=True)

    def to_dict(self):
        return {
            'id':              self.id,
            'fullname':        self.fullname,
            'user_id':         self.user_id,
            'department_id':   self.department_id,
            'department_name': self.department.name if self.department else None,
            'specialization': self.specialization,
            'qualification':   self.qualification,
            'description':     self.description,
            'contact':         self.contact,
            "is_blacklisted": self.user.is_blacklisted if self.user else False,
            'experience':      self.experience,
        }


class Patient(db.Model):
    __tablename__ = 'patient'
    user = db.relationship('User', backref='patient')
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact      = db.Column(db.String(20))
    gender       = db.Column(db.String(10))
    age          = db.Column(db.Integer)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    def to_dict(self):
        return {
            'id':      self.id,
            'name':    self.name,
            'user_id': self.user_id,
            'contact': self.contact,
            'gender':  self.gender,
            'age':     self.age,
            'email':          self.user.email, 
            "is_blacklisted": self.user.is_blacklisted if self.user else False,
        }

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id         = db.Column(db.Integer, primary_key=True)
    doctor_id  = db.Column(db.Integer, db.ForeignKey('doctor.id'),  nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date       = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(100), nullable=False)
    status     = db.Column(db.String(20), default='Booked')  # Booked | Completed | Cancelled
    treatment  = db.relationship('Treatment', backref='appointment', uselist=False)
    cancelled_by = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'doctor_id':    self.doctor_id,
            'doctor_name':  self.doctor.fullname if self.doctor else None,
            'department':   self.doctor.department.name if self.doctor and self.doctor.department else None,
            'patient_id':   self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'date':         str(self.date),
            'time':         self.time,
            'status':       self.status,
            'treatment':    self.treatment.to_dict() if self.treatment else None,
            'cancelled_by': self.cancelled_by,
        }

class Treatment(db.Model):
    __tablename__ = 'treatment'
    id             = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    visit_type     = db.Column(db.String(100))
    test_done      = db.Column(db.String(200))
    diagnosis      = db.Column(db.String(500))
    prescription   = db.Column(db.String(500))
    medicines      = db.Column(db.String(500))
    next_visit     = db.Column(db.String(100))
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id':             self.id,
            'appointment_id': self.appointment_id,
            'visit_type':     self.visit_type,
            'test_done':      self.test_done,
            'diagnosis':      self.diagnosis,
            'prescription':   self.prescription,
            'medicines':      self.medicines,
            'next_visit':     self.next_visit,
            'notes':          self.notes,
            'created_at':     str(self.created_at),
        }

class Availability(db.Model):
    __tablename__ = 'availability'
    id           = db.Column(db.Integer, primary_key=True)
    doctor_id    = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date         = db.Column(db.Date, nullable=False)
    slot         = db.Column(db.String(100), nullable=False)   # e.g. "08:00-12:00"
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'doctor_id':    self.doctor_id,
            'date':         str(self.date),
            'slot':         self.slot,
            'is_available': self.is_available,
        }