from flask import Flask, render_template, jsonify, request, session, url_for, redirect
from google.auth import credentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import json
from requests import get
from werkzeug.security import check_password_hash
from model import db, TeachersLogin, StudentsDB
from bs4 import BeautifulSoup

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
    error=None
    
    if "email" in session:
        return redirect(url_for('updatemarks'))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        dbTeacher = TeachersLogin.query.filter_by(email=email).first()

        if dbTeacher and check_password_hash(dbTeacher.password, password):
            session['email'] = dbTeacher.email
            session['name'] = dbTeacher.name
            session['classes'] = dbTeacher.classes
            session['ip'] = dbTeacher.ip
            session['role'] = dbTeacher.role
            return redirect(url_for('updatemarks'))
        else:
            error="Wrong email or password"

    return render_template('login.html', error=error)


@app.route('/updatemarks', methods=["GET", "POST"])
def updatemarks():

    if "email" in session:
        classes = session['classes']
        data = None

        if request.method == "POST":
            data = request.json

            SUBJECT =  data.get('subject')
            CLASS = data.get('class')
            EXAM = data.get('exam')

            url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Sheet1?key={api}"

            res = get(url)
            if res.status_code == 200:

                jdata = res.json().get('values')
                        

                header = jdata[0]
                name_index = header.index('STUDENTS NAME')
                class_index = header.index('CLASS')
                roll_index = header.index('ROLL')
                subject_index = header.index(f'{EXAM}_{SUBJECT}')
                data = [{
                    'CLASS': row[class_index],
                    'NAME': row[name_index],
                    'ROLL': row[roll_index],
                    'EXAM': EXAM,
                    'SUBJECT': SUBJECT,
                    'SCORE': row[subject_index]
                } for row in jdata[1:] if row[class_index] == CLASS]

                html = render_template('updatemarks.html', data=data)
                soup=BeautifulSoup(html,"lxml")
                content=soup.body.find('div',{'id':'marksTable'}).decode_contents()

                return jsonify({"html":str(content)})
            
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



@app.route('/view', methods=['GET', 'POST'])
def ViewData():
    data = StudentsDB.query.all()
    return render_template('viewdata.html',data=data)


@app.route('/test', methods=["GET", "POST"])
def test():
    error="NO"
    print(render_template('login.html', error=error))
    return "Hello"


if __name__ == '__main__':
    app.run(debug=True)
