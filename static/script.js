document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("selectionForm").addEventListener("change", function() {
        const classValue = document.getElementById("Class").value;
        const subjectValue = document.getElementById("Subject").value;
        const examValue = document.getElementById("Exam").value;

        if (subjectValue !== "Subject" && classValue !== "Class") {
            document.getElementById("submitButton").click();
        }
    });
});

function submit(input) {

    if (input.value < 21 && input.value > -1) {
        submitBTN = input.nextElementSibling
        submitBTN.disabled = true

        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm';
        spinner.setAttribute('role', 'status');
        spinner.setAttribute('aria-hidden', 'true');
        submitBTN.appendChild(spinner);


        const CLASS = input.getAttribute("studentclass");
        const ROLL = input.getAttribute("roll");
        const EXAM = input.getAttribute("exam");

        Update(rows, CLASS, ROLL, EXAM, input.value).then((res) => {

            if (res["STATUS"] === "SUCCESS") {

                submitBTN.disabled = false
                spinner.remove();

                input.classList.remove("is-invalid");
                input.classList.add("is-valid");

                var nextInput = input.closest('tr').nextElementSibling?.querySelector('input');

                if (nextInput) {
                        nextInput.focus();
                        nextInput.scrollIntoView({
                        behavior: "smooth",
                        block: "center",
                        inline: "nearest",
                    });
                }
            } else {input.classList.add("is-invalid")}
        })
    }else {input.classList.add("is-invalid")}

}



async function Update(rows, CLASS, ROLL, EXAM, value) {
    const keys = rows[0]
    const CLASSIndex = keys.indexOf("CLASS")        
    const ROLLIndex = keys.indexOf("ROLL")

    const EXAMIndex = keys.indexOf(EXAM)+1  //EXAM HERE.....
    const rowIndex = rows.findIndex(row => row[CLASSIndex] === CLASS && row[ROLLIndex] == ROLL)+1

    if (CLASSIndex === -1 || ROLLIndex === -1 || EXAMIndex === 0 || rowIndex === 0) {
        console.error('Error: Invalid CLASS, ROLL, or EXAM column.');
        return {"STATUS": "FAILED"}}

    console.log(EXAMIndex , rowIndex)


    const range = "Sheet1!"+String.fromCharCode(64 + EXAMIndex)+rowIndex

    const toUpdate = {"range": range,"value": value}

    try {
        const response = await fetch("/update", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(toUpdate)
        })

        const res = await response.json();
        return res;
    } catch (error) {
        console.error('Error:', error);
        return {"STATUS": "FAILED"};
    }

}


async function loadData() {
  var url ="https://sheets.googleapis.com/v4/spreadsheets/1yGyqIyDWtaVK1z2LbvvtEDl1YpeIgWMwuAyUcIdr3Cc/values/Sheet1?key=AIzaSyCunanUcxEoloBYJR1EqhkD16-uWAxlQzY";

  try {
      const response = await fetch(url);
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      const jdata = await response.json();
      const rows = jdata.values;



      return rows
  } catch (error) {
      console.log(error);
  }
}

loadData().then((fetchData) => {rows = fetchData});

document.addEventListener("keydown", (event) => {

    input = document.activeElement

    if (event.key === "Enter" && input.tagName === 'INPUT'){
        event.preventDefault()
        submit(input)

    }
});




/*function SelectFunc() {
  const CLASS = document.getElementById("Class").value;
  const SUBJECT = document.getElementById("Subject").value;

  if (SUBJECT !== "Subject" && CLASS !== "Class") {
      var tbody = document.getElementById("tableBody");

      while (tbody.firstChild) {
          tbody.removeChild(tbody.firstChild)}

          loadData().then((rows) => {

              if (rows != null) {

                  creatingRows(rows, CLASS, SUBJECT)
              }
          });      
  }
}

async function loadData() {
  var url ="https://sheets.googleapis.com/v4/spreadsheets/1yGyqIyDWtaVK1z2LbvvtEDl1YpeIgWMwuAyUcIdr3Cc/values/Sheet1?key=AIzaSyCunanUcxEoloBYJR1EqhkD16-uWAxlQzY";

  try {
      const response = await fetch(url);
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      const jdata = await response.json();
      const rows = jdata.values;



      return rows
  } catch (error) {
      console.log(error);
  }
}

loadData().then((fetchData) => {rows = fetchData});


function creatingRows(rows, CLASS, SUBJECT) {

    const exam_col = "FA1_" + SUBJECT
    const keys = rows[0]
    
    const Data = rows.slice(1).map(row => 
        Object.fromEntries(keys.map((key, index) => 
            [key, row[index]])))

    const data = Data.filter((item) => item.CLASS === CLASS)
    const table = document.getElementById("tableBody");

    for (let i = 0; i < data.length; i++) {
        
    
        const row = data[i];
        //Creating Row for all the students in 11 sets
        const rowElement = document.createElement("tr");
    
        //Creating table data of class
        const tdClass = document.createElement("td");
        tdClass.setAttribute("data-label", "Class");
        tdClass.textContent = row.CLASS;
    
        const tdRoll = document.createElement("td");
        tdRoll.setAttribute("data-label", "Roll no");
    
        tdRoll.textContent = row.ROLL;
    
        //Creating table data of Marks Input
        const tdMarks = document.createElement("td");
        const inputField = document.createElement("input");
        const submitButton = document.createElement("button");
        const InputButtonDIV = document.createElement("div");
          
        InputButtonDIV.setAttribute("class", "input-group")
    
        inputField.setAttribute("type" ,"number");
        inputField.setAttribute("inputmode", "numeric");
        inputField.setAttribute("placeholder", row.CLASS+" " + SUBJECT + " MARKS");
        inputField.setAttribute("class", "form-control");
        inputField.setAttribute("onFocus", "this.select()");
        inputField.setAttribute("value", row[exam_col]);
        inputField.setAttribute("studentclass", row.CLASS);
        inputField.setAttribute("roll",row.ROLL);
        inputField.setAttribute("exam",exam_col);
    
        submitButton.setAttribute("type", "submit")
        submitButton.setAttribute("class", "btn btn-primary")
        submitButton.setAttribute("onclick", "submit(this.previousElementSibling)")
        submitButton.textContent = 'SUBMIT';  
          
        InputButtonDIV.appendChild(inputField);
        InputButtonDIV.appendChild(submitButton);
    
        tdMarks.appendChild(InputButtonDIV);
 
          //Start appending td in rows
        rowElement.appendChild(tdClass);
        rowElement.appendChild(tdRoll);
        rowElement.appendChild(tdMarks);
    
        table.appendChild(rowElement);
  }
}*/

