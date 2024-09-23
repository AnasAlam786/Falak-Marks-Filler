from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TeachersLogin(db.Model):
  
    __tablename__ = 'TeachersLogin'
  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    classes = db.Column(db.JSON, nullable=False)
    ip = db.Column(db.JSON)
    role = db.Column(db.Text, nullable=False)

class StudentsDB(db.Model):
  
    __tablename__ = 'StudentsDB'
  
    id = db.Column(db.Integer, primary_key=True)
    
    STUDENTS_NAME	= db.Column(db.Text, nullable=False)
    DOB	= db.Column(db.Date)
    CLASS	= db.Column(db.Text, nullable=False)
    ROLL	= db.Column(db.Integer, nullable=False)
    PHONE	= db.Column(db.Text)
    PEN	= db.Column(db.Text)
    GENDER	= db.Column(db.Text, nullable=False)
    SR	= db.Column(db.Integer)
    ADDRESS	= db.Column(db.Text)
    HEIGHT	= db.Column(db.Integer)
    WEIGHT	= db.Column(db.Integer)
    CAST	= db.Column(db.Text)
    RELIGION	= db.Column(db.Text)
    PIN = db.Column(db.Text)
    IMAGE = db.Column(db.Text)
    AADHAAR	= db.Column(db.Text)
    FATHERS_NAME	= db.Column(db.Text)
    MOTHERS_NAME	= db.Column(db.Text)
    Intialised_at_SDMS	= db.Column(db.Text)
    ADMISSION_NO	= db.Column(db.Integer)
    ADNISSION_DATE = db.Column(db.Date)
  
    @property
    def formatted_dob(self):
        return self.DOB.strftime("%a, %B %d, %Y") if self.DOB else None
    
