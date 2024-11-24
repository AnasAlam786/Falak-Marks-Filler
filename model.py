from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified


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
    ADMISSION_DATE = db.Column(db.Date)
    FA1 = db.Column(db.JSON)
    SA1 = db.Column(db.JSON)
    FA2 = db.Column(db.JSON)
    SA2 = db.Column(db.JSON)
    Fees = db.Column(db.JSON)

    __table_args__ = (
        db.Index('idx_class_roll', 'CLASS', 'ROLL'),
    )

def updateScore(id, exam, subject, score):
    student = StudentsDB.query.filter_by(id=id).first()

    if student:
        student_data = getattr(student, exam)  # Retrieve the JSON object
        student_data[subject] = score  # Modify the JSON object with the new score
        setattr(student, exam, student_data)  # Reassign the modified JSON back to the column
        flag_modified(student, exam)  # Flag the JSON column as modified
        db.session.commit()
        return "SUCCESS"
    else:
        return "FAILED"

def StudentData(*args, class_filter_json=None):
    # Class order mapping for post-query sorting
    class_order_mapping = {
        'Nursery/KG/PP3': 1, 'LKG/KG1/PP2': 2,
        'UKG/KG2/PP1': 3, '1st': 4,
        '2nd': 5, '3rd': 6,
        '4th': 7, '5th': 8,
        '6th': 9, '7th': 10, '8th': 11
    }

    # Determine columns to select; include 'CLASS' by default
    selected_columns = [getattr(StudentsDB, col) for col in args if hasattr(StudentsDB, col)]
    if not any(col.key == 'CLASS' for col in selected_columns):
        selected_columns.append(StudentsDB.CLASS)

    # Construct query with selected columns
    query = StudentsDB.query.with_entities(*selected_columns)

    # Apply class filter if provided
    if class_filter_json and 'CLASS' in class_filter_json:
        query = query.filter(StudentsDB.CLASS.in_(class_filter_json['CLASS']))

    # Order results directly in the query
    query = query.order_by(StudentsDB.CLASS.asc(), StudentsDB.ROLL.asc()).yield_per(1000)

    # Fetch all results
    results = query.all()

    # Map the selected column names to their values in each row
    column_names = [col.key for col in selected_columns]  # Get the names of selected columns
    results_json = [
        dict(zip(column_names, row)) for row in results
    ]

    # Sort by class order mapping
    results_json.sort(key=lambda row: (class_order_mapping.get(row['CLASS'], float('inf')), row['ROLL']))

    return results_json
