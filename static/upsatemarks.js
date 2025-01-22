document.addEventListener("DOMContentLoaded", function () {
    const classDropdown = document.getElementById("Class");
    const subjectDropdown = document.getElementById("Subject");
    const ExamDropdown = document.getElementById("Exam");

    

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

    const exam = input.getAttribute("exam");
    const subject = input.getAttribute("subject");
    const id = input.getAttribute("student_id");
    
    if (
        ((exam === "FA1" || exam === "FA2") && input.value >= 0 && input.value <= 20) ||
        ((exam === "SA1" || exam === "SA2") && input.value >= 0 && input.value <= 80) || 
        (subject==="Drawing" && ["A", "B", "C","D","E"].includes(input.value)) ||
        (exam==="Attendance" && input.value >= 0 && input.value <= 250)
        
      ) {
        submitBTN = input.nextElementSibling
        submitBTN.disabled = true

        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm';
        spinner.setAttribute('role', 'status');
        spinner.setAttribute('aria-hidden', 'true');
        submitBTN.appendChild(spinner);


        

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

document.addEventListener("keydown", (event) => {

    input = document.activeElement

    if (event.key === "Enter" && input.tagName === 'INPUT'){
        event.preventDefault()
        submit(input)

    }
});
