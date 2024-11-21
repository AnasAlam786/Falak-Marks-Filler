document.addEventListener("DOMContentLoaded", function() {
    function updateOptions() {
        var classValue = document.getElementById("Class").value;
        var subject = document.getElementById("Subject");
        var subjectOptions = subject.options;
        var disableSubjects = ['SCIENCE', 'COMPUTER', 'GK', 'SST', 'DRAWING'];
        var disableClasses = ['Nursery/KG/PP3', 'LKG/KG1/PP2', 'UKG/KG2/PP1'];
        

        // Enable all subject options first
        for (var i = 0; i < subjectOptions.length; i++) {
            subjectOptions[i].disabled = false;
        }

        // Disable options based on class selection
        if (disableClasses.includes(classValue)) {
            for (var i = 0; i < subjectOptions.length; i++) {
                var option = subjectOptions[i];
                if (disableSubjects.includes(option.value)) {
                    option.disabled = true;
                }
            }
        }

        // Enable all options again before disabling based on subject selection
        var classOptions = document.getElementById("Class").options;
        for (var i = 0; i < classOptions.length; i++) {
            classOptions[i].disabled = false;
        }

        var subjectValue = document.getElementById("Subject").value;
        if (disableSubjects.includes(subjectValue)) {
            for (var i = 0; i < classOptions.length; i++) {
                var option = classOptions[i];
                if (disableClasses.includes(option.value)) {
                    option.disabled = true;
                }
            }
        }
    }

    document.getElementById("selectionForm").addEventListener("change", updateOptions);
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
