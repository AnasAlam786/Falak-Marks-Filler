from flask import Flask, render_template, jsonify, request, session, url_for, redirect
from google.auth import credentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import json
from requests import get
from werkzeug.security import check_password_hash
from model import db, TeachersLogin, StudentData, updateScore
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
            payload = request.json

            SUBJECT =  payload.get('subject')
            CLASS = payload.get('class')
            EXAM = payload.get('exam')

            data = StudentData("id","STUDENTS_NAME","ROLL",EXAM, class_filter_json = {"CLASS": [CLASS]})
 
            html = render_template('updatemarks.html', data=data, SUBJECT=SUBJECT, EXAM=EXAM)
            soup=BeautifulSoup(html,"lxml")
            content=soup.body.find('div',{'id':'marksTable'}).decode_contents()

            return jsonify({"html":str(content)})
            
        return render_template('updatemarks.html', data=data, classes=classes)

    else:
        return redirect(url_for('login'))
        



@app.route('/update', methods=['POST'])
def update():

    data = request.json
    
    subject = data.get('subject')
    exam = data.get('exam')
    score = data.get('value')
    id = data.get('id')

    resp = updateScore(id, exam, subject, score)

    return jsonify({"STATUS": resp})


@app.route('/students', methods=['GET', 'POST'])
def studentsData():
    data = StudentData("STUDENTS_NAME","DOB","CLASS","ROLL","PHONE","IMAGE","ADMISSION_NO","FATHERS_NAME")
    
    
    if request.method == "POST":
        payload = request.json

        CLASS =  payload.get('CLASS')

        if CLASS=="All":
            html = render_template('students.html', data=data)
            soup=BeautifulSoup(html,"lxml")
            content=soup.body.find('div',{'id':'StudentData'}).decode_contents()

            return jsonify({"html":str(content)})

        else:
            data = [row for row in data if row.CLASS == CLASS]

            html = render_template('students.html', data=data)
            soup=BeautifulSoup(html,"lxml")
            content=soup.body.find('div',{'id':'StudentData'}).decode_contents()

            return jsonify({"html":str(content)})


    return render_template('students.html',data=data)


@app.route('/entrycard')
def entryCard():


    data = StudentData("STUDENTS_NAME","FATHERS_NAME","CLASS","ROLL","DOB","PHONE","IMAGE")
    print(type(data[0].DOB))

    data = [data[i:i + 4] for i in range(0, len(data), 4)]


    logo='https://lh3.googleusercontent.com/d/1w4v4yf1NTRjrzoyYnA3PTEShS7rBaQiY=s300'
    school="FALAK PUBLIC SCHOOL"
    year="2024-25"
    exam="SA1"
    quality = "200"

    return render_template('admit.html', data=data, school=school, year=year, exam=exam, logo=logo,quality=quality)



@app.route('/seatChits')
def seatChits():

    result = StudentData("STUDENTS_NAME","FATHERS_NAME","CLASS","ROLL")
    fitlerData = [row for row in result if row.CLASS not in ['Nursery/KG/PP3', 'LKG/KG1/PP2','UKG/KG2/PP1']]
    data = [fitlerData[i:i + 28] for i in range(0, len(fitlerData), 28)]
    

    return render_template('seatChits.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
    
