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
            SUBJECT = request.form.get('selectSubject')
            CLASS = request.form.get('selectClass')
            EXAM = request.form.get('selectExam')

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
    data = StudentsDB.query.filter_by(CLASS="I")
    return render_template('viewdata.html',data=data)


if __name__ == '__main__':
    app.run(debug=True)
    
"""
GOOGLE_SHEETS_URL = "https://sheets.googleapis.com/v4/spreadsheets/1yGyqIyDWtaVK1z2LbvvtEDl1YpeIgWMwuAyUcIdr3Cc/values/Sheet1?key=AIzaSyCunanUcxEoloBYJR1EqhkD16-uWAxlQzY"

@app.route('/getData/<CLASS>/<SUBJECT>',methods=['GET','POST'])
def getData(CLASS, SUBJECT):
    response = requests.get(GOOGLE_SHEETS_URL)

    if response.status_code == 200:
        jdata = response.json().get('values')
        df = pd.DataFrame(jdata[1:], columns=jdata[0])
        exam=f"FA1_{SUBJECT}"

        filtered_df = df[df['CLASS'] == CLASS]
        data = filtered_df[['CLASS', 'ROLL', exam]].to_dict(orient='records')
        return jsonify(data)
    else:
        return "Failed"
    return f"Class is {CLASS}"



function SelectFunc() {
          const CLASS = document.getElementById("Class").value;
          const SUBJECT = document.getElementById("Subject").value;

          if (SUBJECT !== "Subject" && CLASS !== "Class") {

            fetch(`/getData/${CLASS}/${SUBJECT}`,{method: 'GET',
                 headers: {
                     'Content-Type': 'application/json'}
                 })
            .then(response => response.json())
            .then(data => {
              creatingRows(data, SUBJECT)
              onEnter()
            })
            console.log("Hii there")
          }


        }  




function onEnter(rows) {
        focusedInput = document.activeElement

        if (focusedInput && focusedInput.tagName === 'INPUT') {

        focusedInput.addEventListener("keydown", (event) => {

            if (event.key === "Enter") {
                event.preventDefault()
                button=focusedInput.nextElementSibling
                submit(button)


            }
        });
    }
}"""
