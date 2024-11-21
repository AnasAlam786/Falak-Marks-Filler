document.addEventListener("DOMContentLoaded", function () {
    const classDropdown = document.getElementById("Class");
    const subjectDropdown = document.getElementById("Subject");

    // Define mappings for mutual exclusions
    const restrictedClasses = ["Nursery/KG/PP3", "LKG/KG1/PP2", "UKG/KG2/PP1"];
    const restrictedSubjects = ["Science", "Computer", "SST"];

    classDropdown.addEventListener("change", function () {
      const selectedClass = classDropdown.value;

      // Enable all subject options first
      Array.from(subjectDropdown.options).forEach(option => {
        option.disabled = false;
      });

      // Disable restricted subjects if restricted class is selected
      if (restrictedClasses.includes(selectedClass)) {
        restrictedSubjects.forEach(subject => {
          const option = Array.from(subjectDropdown.options).find(opt => opt.value === subject);
          if (option) option.disabled = true;
        });
      }
    });

    subjectDropdown.addEventListener("change", function () {
      const selectedSubject = subjectDropdown.value;

      // Enable all class options first
      Array.from(classDropdown.options).forEach(option => {
        option.disabled = false;
      });

      // Disable restricted classes if restricted subject is selected
      if (restrictedSubjects.includes(selectedSubject)) {
        restrictedClasses.forEach(cls => {
          const option = Array.from(classDropdown.options).find(opt => opt.value === cls);
          if (option) option.disabled = true;
        });
      }
    });
  });

function submit(input) {

    if (input.value < 81 && input.value > -1) {
        submitBTN = input.nextElementSibling
        submitBTN.disabled = true

        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm';
        spinner.setAttribute('role', 'status');
        spinner.setAttribute('aria-hidden', 'true');
        submitBTN.appendChild(spinner);


        const id = input.getAttribute("student_id");
        const exam = input.getAttribute("exam");
        const subject = input.getAttribute("subject");

        fetch("/update", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: id,
                subject: subject,
                exam: exam,
                value: input.value
            })
        })
        .then(response => response.json())
        .then(res => {
            if (res["STATUS"] === "SUCCESS") {
                submitBTN.disabled = false;
                spinner.remove();
        
                input.classList.remove("is-invalid");
                input.classList.add("is-valid");
        
                // Move focus to the next input in the table row
                const nextInput = input.closest('tr').nextElementSibling?.querySelector('input');
                
                if (nextInput) {
                    nextInput.focus();
                    nextInput.scrollIntoView({
                        behavior: "smooth",
                        block: "center",
                        inline: "nearest",
                    });
                }
            } else {
                input.classList.add("is-invalid");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            input.classList.add("is-invalid");
        });        
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


document.addEventListener("keydown", (event) => {

    input = document.activeElement

    if (event.key === "Enter" && input.tagName === 'INPUT'){
        event.preventDefault()
        submit(input)

    }
});
