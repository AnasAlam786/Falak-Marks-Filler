from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case

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
    STUDENTS_NAME = db.Column(db.Text, nullable=False)
    DOB = db.Column(db.Date)
    CLASS = db.Column(db.Text, nullable=False)
    ROLL = db.Column(db.Integer, nullable=False)
    PHONE = db.Column(db.Text)
    PEN = db.Column(db.Text)
    GENDER = db.Column(db.Text, nullable=False)
    SR = db.Column(db.Integer)
    ADDRESS = db.Column(db.Text)
    HEIGHT = db.Column(db.Integer)
    WEIGHT = db.Column(db.Integer)
    CAST = db.Column(db.Text)
    RELIGION = db.Column(db.Text)
    PIN = db.Column(db.Text)
    IMAGE = db.Column(db.Text)
    AADHAAR = db.Column(db.Text)
    FATHERS_NAME = db.Column(db.Text)
    MOTHERS_NAME = db.Column(db.Text)
    Intialised_at_SDMS = db.Column(db.Text)
    ADMISSION_NO = db.Column(db.Integer)
    ADNISSION_DATE = db.Column(db.Date)

    __table_args__ = (
        db.Index('idx_class_roll', 'CLASS', 'ROLL'),
    )

def StudentData(*args):
    class_order_mapping = {
        'Nursery/KG/PP3': 1, 'LKG/KG1/PP2': 2,
        'UKG/KG2/PP1': 3, '1st': 4,
        '2nd': 5, '3rd': 6,
        '4th': 7, '5th': 8,
        '6th': 9, '7th': 10, '8th': 11
    }

    # Prepare the case expression for class ordering
    order_case = case(
        *[(StudentsDB.CLASS == class_name, order) for class_name, order in class_order_mapping.items()]
    )

    # Fetch only the necessary columns or all columns if none are specified
    selected_columns = [getattr(StudentsDB, col) for col in args] if args else [*StudentsDB.__table__.columns]

    # Format the DOB in SQL query itself
    formatted_columns = [
        func.to_char(StudentsDB.DOB, 'Dy, Month DD, YYYY').label('DOB') if col.name == 'DOB' else col
        for col in selected_columns
    ]

    # Fetch the results using efficient query
    results = (StudentsDB.query
               .with_entities(*formatted_columns)
               .order_by(order_case, StudentsDB.ROLL.asc())
               .yield_per(1000)  # Efficiently process data in batches
               .all())

    return results
