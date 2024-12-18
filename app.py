from flask import Flask, render_template, jsonify, request, session, url_for, redirect
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from model import db, TeachersLogin, StudentData, updateScore, updateFees, StudentsDB, FeesDB ,updateParentsAdhar
from bs4 import BeautifulSoup
import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    error=None
    
    if "email" in session:
        return redirect(url_for('studentsData'))

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
            session.permanent = True
            return redirect(url_for('studentsData'))
        else:
            error="Wrong email or password"

    return render_template('login.html', error=error)


@app.route('/studentModal', methods=["GET", "POST"])
def studentModal():
    return render_template('studentModal.html')


@app.route('/getfees', methods=["GET", "POST"])
def getfees():

    if request.method == "POST":
        #Paying Fees
        req = request.json
        id = req.get('studentId')

        if req.get('task') =='update':
            months = req.get('months')
            current_date = datetime.datetime.now().strftime("%d-%m-%Y")

            resp=updateFees(id, months=months, date=current_date, extra=None)
            return jsonify({"STATUS": resp})
        
        elif req.get('task') =='get':
            student = StudentsDB.query.filter_by(id=id).first()
            data=StudentsDB.query.filter_by(PHONE=student.PHONE).all()
            data=[record.to_dict() for record in data]

            for sibling in data:
                Fee=FeesDB.query.filter_by(CLASS=sibling["CLASS"]).first().Fee
                sibling["Fee"]=Fee
                            
            monthName =  datetime.datetime.now().strftime("%B")
            monthIndex=list(data[0]["Fees"].keys()).index(monthName)+1

            html = render_template('feesModal.html',data=data,currentMonth=monthIndex)
            soup=BeautifulSoup(html,"lxml")
            content=soup.body.decode_contents()
            
            return jsonify({"html":str(content),"data":data})

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
    if "email" in session:
        data = StudentData("id","STUDENTS_NAME","DOB","CLASS","ROLL","PHONE","IMAGE","FATHERS_NAME","Fees")
        """data = StudentsDB.query.with_entities(StudentsDB.STUDENTS_NAME, StudentsDB.DOB, StudentsDB.PHONE, 
                                              StudentsDB.ROLL, StudentsDB.CLASS, StudentsDB.Fees,
                                              StudentsDB.id, StudentsDB.IMAGE,StudentsDB.FATHERS_NAME).all()"""
        for student in data:
            student['DOB'] = student['DOB'].strftime('%d %B %Y')

        
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
    else:
        return redirect(url_for('login'))

@app.route('/entrycard')
def entryCard():
    if "email" in session:

        data = StudentData("STUDENTS_NAME","FATHERS_NAME","CLASS","ROLL","DOB","PHONE","IMAGE")

        data = [data[i:i + 4] for i in range(0, len(data), 4)]


        logo='https://lh3.googleusercontent.com/d/1w4v4yf1NTRjrzoyYnA3PTEShS7rBaQiY=s300'
        school="FALAK PUBLIC SCHOOL"
        year="2024-25"
        exam="SA1"
        quality = "200"

        return render_template('admit.html', data=data, school=school, year=year, exam=exam, logo=logo,quality=quality)
    else:
        return redirect(url_for('login'))

@app.route('/seatChits')
def seatChits():
    if "email" in session:
        result = StudentData("STUDENTS_NAME","FATHERS_NAME","CLASS","ROLL")
        fitlerData = [row for row in result if row["CLASS"] not in ['Nursery/KG/PP3', 'LKG/KG1/PP2','UKG/KG2/PP1']]
        data = [fitlerData[i:i + 28] for i in range(0, len(fitlerData), 28)]
        
        return render_template('seatChits.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/marks', methods=["GET","POST"])
def marks():
    if "email" in session:
        Data = None

        if request.method == "POST":

            CLASS = request.json.get('class')

            Data = StudentData("STUDENTS_NAME","ROLL","FATHERS_NAME", "FA1", "FA2", "SA1", "SA2", class_filter_json = {"CLASS": [CLASS]})

            for student in Data:
            # Add 'Total' to each FA1, FA2, SA1, and SA2
                for key in ['FA1', 'FA2', 'SA1', 'SA2']:
                    scores = student[key]
                    total = sum(int(value) for value in scores.values() if value.isdigit())
                    scores['Total'] = total

                # Calculate FA1_SA1 (Sum of FA1 and SA1)
                fa1_sa1 = {}
                for subject in student['FA1']:
                    if subject != 'Total':
                        fa1_value = int(student['FA1'].get(subject, 0)) if student['FA1'].get(subject, '').isdigit() else 0
                        sa1_value = int(student['SA1'].get(subject, 0)) if student['SA1'].get(subject, '').isdigit() else 0
                        fa1_sa1[subject] = str(fa1_value + sa1_value)
                fa1_sa1['Total'] = sum(int(value) for value in fa1_sa1.values() if value.isdigit())
                student['FA1_SA1'] = fa1_sa1

                # Calculate FA2_SA2 (Sum of FA2 and SA2)
                fa2_sa2 = {}
                for subject in student['FA2']:
                    if subject != 'Total':
                        fa2_value = int(student['FA2'].get(subject, 0)) if student['FA2'].get(subject, '').isdigit() else 0
                        sa2_value = int(student['SA2'].get(subject, 0)) if student['SA2'].get(subject, '').isdigit() else 0
                        fa2_sa2[subject] = str(fa2_value + sa2_value)
                fa2_sa2['Total'] = sum(int(value) for value in fa2_sa2.values() if value.isdigit())
                student['FA2_SA2'] = fa2_sa2

                # Calculate Grand_Total (Sum of all scores across FA1, FA2, SA1, and SA2)
                grand_total = {}
                for subject in student['FA1']:
                    if subject != 'Total':
                        total_value = sum(
                            int(student[key].get(subject, 0)) if student[key].get(subject, '').isdigit() else 0
                            for key in ['FA1', 'FA2', 'SA1', 'SA2']
                        )
                        grand_total[subject] = str(total_value)
                grand_total['Total'] = sum(int(value) for value in grand_total.values() if value.isdigit())
                student['Grand_Total'] = grand_total

            html = render_template('showMarks.html', Data=Data)
            soup=BeautifulSoup(html,"lxml")
            content=soup.body.find('div',{'id':'results'}).decode_contents()

            return jsonify({"html":str(content)})
        
        return render_template('showMarks.html', Data=Data)
    
    else:
        return redirect(url_for('login'))

@app.route('/aapar', methods=["GET", "POST"])
def aapar():

    if "email" in session:
        data = StudentData("id","STUDENTS_NAME","ROLL", "FATHERS_NAME","MOTHERS_NAME","Parents_Aadhar","CLASS")

        if request.method == "POST":
            payload = request.json

            if payload.get('task')=='pageUpdate':

                CLASS = payload.get('class')

                data = StudentData("id","STUDENTS_NAME","ROLL", "FATHERS_NAME","MOTHERS_NAME","Parents_Aadhar",class_filter_json = {"CLASS": [CLASS]})
    
                html = render_template('aapar.html', data=data)
                soup=BeautifulSoup(html,"lxml")
                content=soup.body.find('div',{'id':'dataTable'}).decode_contents()

                return jsonify({"html":str(content)})
            
            elif payload.get('task')=='aadhar':
                id=payload.get('id')
                mother=payload.get('Mother_Aadhar').replace("-","")
                father=payload.get('Father_Aadhar').replace("-","")
                data={}

                
                if (father=='' or len(father)==12):
                    data["Father"]=father
                else:
                    return {"STATUS": 'FAILED'}
                    
                if (mother=='' or len(mother)==12):
                    data["Mother"]=mother
                else:
                    return {"STATUS": 'FAILED'}
                
                
                result = updateParentsAdhar(id, data)
                return{"STATUS": result}
            
        return render_template('aapar.html', data=data)

    else:
        return redirect(url_for('login'))

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
