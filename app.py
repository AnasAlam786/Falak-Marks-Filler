from flask import Flask, render_template, jsonify, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from google.auth import credentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import json
from requests import get
from werkzeug.security import check_password_hash

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SESSION_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class TeachersLogin(db.Model):
    __tablename__ = 'TeachersLogin'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    classes = db.Column(db.JSON, nullable=False)
    ip = db.Column(db.JSON)
    role = db.Column(db.Text, nullable=False)


SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
credentials = json.loads(os.getenv('CREDENTIALS'))
api = os.getenv('API_KEY')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect(url_for('updatemarks'))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        dbTeacher = TeachersLogin.query.filter_by(email=email).first()

        if dbTeacher:
            if check_password_hash(dbTeacher.password, password):
                session['email'] = dbTeacher.email
                session['name'] = dbTeacher.name
                session['classes'] = dbTeacher.classes
                session['ip'] = dbTeacher.ip
                session['role'] = dbTeacher.role
                return redirect(url_for('updatemarks'))

    else:
        return render_template('login.html')


@app.route('/updatemarks', methods=["GET", "POST"])
def updatemarks():
    if "email" in session:
        classes = session['classes']

        data = None

        if request.method == "POST":
            SUBJECT = request.form.get('selectSubject')
            CLASS = request.form.get('selectClass')
            EXAM = request.form.get('selectExam')

            url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Sheet1?key={api}"

            res = get(url)
            if res.status_code == 200:

                jdata = res.json().get('values')

                header = jdata[0]
                class_index = header.index('CLASS')
                roll_index = header.index('ROLL')
                subject_index = header.index(f'{EXAM}_{SUBJECT}')

                #print(class_index, roll_index, subject_index)

                data = [{
                    'CLASS': row[class_index],
                    'ROLL': row[roll_index],
                    'EXAM': EXAM,
                    'SUBJECT': SUBJECT,
                    'SCORE': row[subject_index]
                } for row in jdata[1:] if row[class_index] == CLASS]

        return render_template('updatemarks.html', data=data, classes=classes)

    else:
        return redirect(url_for('login'))


@app.route('/update', methods=['POST'])
def update():

    data = request.json

    if (data["value"]) == "":
        body = {'values': [[data["value"]]]}
    else:
        body = {'values': [[int(data["value"])]]}

    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=data["range"],
            valueInputOption='RAW',
            body=body).execute()
        return jsonify({"STATUS": "SUCCESS"})

    except Exception as e:
        return jsonify({"STATUS": "FAILED", "ERROR": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
