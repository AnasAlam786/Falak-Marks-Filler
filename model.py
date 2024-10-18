from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import case
from collections import namedtuple

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

def StudentData(*args):
    class_order = [
        ('Nursery/KG/PP3', 1), ('LKG/KG1/PP2', 2),
        ('UKG/KG2/PP1', 3), ('1st', 4),
        ('2nd', 5), ('3rd', 6),
        ('4th', 7), ('5th', 8),
        ('6th', 9), ('7th', 10),('8th', 11)]

    order_case = case(*[(StudentsDB.CLASS == name, order) for name, order in class_order])
    selected_columns = [getattr(StudentsDB, col) for col in args] if args else [*StudentsDB.__table__.columns]

    results = (StudentsDB.query
               .with_entities(*selected_columns)
               .order_by(order_case, StudentsDB.ROLL.asc())
               .all())

    # Create a named tuple and format date fields
    Result = namedtuple('Result', [col.name for col in selected_columns])

    return [Result(*(field.strftime('%a, %B %d, %Y') if isinstance(field, datetime) else field for field in row)) for row in results]
