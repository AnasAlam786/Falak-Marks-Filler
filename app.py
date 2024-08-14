from flask import Flask, render_template, jsonify, request
from google.auth import credentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import json
from requests import get


app = Flask(__name__)

load_dotenv()
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
credentials = json.loads(os.getenv('CREDENTIALS'))
api = os.getenv('API_KEY')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/updatemarks',methods=["GET","POST"])
def updatemarks():
    data=None
    
    if request.method == "POST":
        SUBJECT=request.form.get('selectSubject')
        CLASS=request.form.get('selectClass')
        EXAM=request.form.get('selectExam')

        url=f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Sheet1?key={api}"
        
        res = get(url)
        if res.status_code == 200:
            
            jdata = res.json().get('values')
            
            header = jdata[0]
            class_index = header.index('CLASS')
            roll_index = header.index('ROLL')
            subject_index = header.index(f'{EXAM}_{SUBJECT}')

            #print(class_index, roll_index, subject_index)

            data = [
                {
                    'CLASS': row[class_index],
                    'ROLL': row[roll_index],
                    'EXAM': EXAM,
                    'SUBJECT': SUBJECT,
                    'SCORE': row[subject_index]
                }
                for row in jdata[1:] if row[class_index] == CLASS
            ]


            
            
    return render_template('updatemarks.html',data=data)


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
