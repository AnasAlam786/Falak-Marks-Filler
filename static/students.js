  const classSelect = document.getElementById('classView');
  const searchInput = document.getElementById('search-input');
  const itemsPerPageSelect = document.getElementById('items-per-page');
  const studentCards = Array.from(document.getElementById('StudentData').children);
  const loadMoreBtn = document.getElementById('load-more');

  let itemsPerPage = parseInt(itemsPerPageSelect.value, 10);
  let currentVisibleItems = 0;
  let filteredStudents = [];

  // Function to batch-update the DOM for better performance
  function showStudents(students, start, count) {
    const fragment = document.createDocumentFragment();
    for (let i = start; i < start + count && i < students.length; i++) {
      students[i].style.display = 'block';
      fragment.appendChild(students[i]);
    }
    document.getElementById('StudentData').appendChild(fragment);
    currentVisibleItems += count;
  }

  // Function to apply filters and pagination
  function filterStudents() {
    const selectedClass = classSelect.value.toLowerCase();
    const searchText = searchInput.value.toLowerCase();

    filteredStudents = studentCards.filter(function (student) {
      const studentName = student.querySelector('.student-name').textContent.toLowerCase();
      const studentClassRoll = student.querySelector('.student-class-roll').textContent.toLowerCase();
      const studentFather = student.querySelector('.student-father').textContent.toLowerCase();
      const studentClass = studentClassRoll.split(' - ')[0];

      // Filter logic: match class and name/roll/father's name search
      const classMatch = selectedClass === 'all' || studentClass === selectedClass;
      const searchMatch = studentName.includes(searchText) ||
                          studentClassRoll.includes(searchText) ||
                          studentFather.includes(searchText);

      return classMatch && searchMatch;
    });

    // Hide all students first
    studentCards.forEach(student => student.style.display = 'none');

    // Show the first batch of students
    currentVisibleItems = 0;
    showStudents(filteredStudents, 0, itemsPerPage);

    // Show or hide the Load More button
    if (filteredStudents.length > itemsPerPage) {
      loadMoreBtn.style.display = 'block';
    } else {
      loadMoreBtn.style.display = 'none';
    }
  }

  // Load more students when the button is clicked
  function loadMoreStudents() {
    if (currentVisibleItems < filteredStudents.length) {
      const remainingItems = filteredStudents.length - currentVisibleItems;
      const itemsToLoad = Math.min(itemsPerPage, remainingItems);
      showStudents(filteredStudents, currentVisibleItems, itemsToLoad);

      if (currentVisibleItems >= filteredStudents.length) {
        loadMoreBtn.style.display = 'none';
      }
    }
  }

  // Event listeners
  classSelect.addEventListener('change', filterStudents);
  searchInput.addEventListener('input', filterStudents);
  itemsPerPageSelect.addEventListener('change', function () {
    itemsPerPage = parseInt(itemsPerPageSelect.value, 10);
    filterStudents();
  });

  loadMoreBtn.addEventListener('click', loadMoreStudents);

  // Initial load
  filterStudents();

  let sharedData=null
  function viewStudentDetails(studentId) {
    document.getElementById('modalBody').innerHTML = '';
    new bootstrap.Modal(document.getElementById('feesModal')).show()
    updatePage('/getfees', 'modalBody',   {studentId: studentId, task: 'get' }).then((data) => {
      sharedData=data
    
      const grandTotal = document.getElementById('grandTotal');
      const contentSections = document.querySelectorAll('[id^="contentSection"]');
      const toggleTriangles = document.querySelectorAll('[id^="toggleTriangle"]');
      const checkedMonths = document.querySelectorAll('[id^="checkedMonths"]');
      const netAmounts = document.querySelectorAll('[id^="netAmount"]')

      contentSections.forEach((contentSection, index) => {
        months=0
        const toggleTriangle = toggleTriangles[index];
    
        contentSection.addEventListener('show.bs.collapse', () => {
          toggleTriangle.style.borderTop = 'none';
          toggleTriangle.style.borderBottom = '8px solid white';
    
          contentSections.forEach((section) => {
            if (section !== contentSection) {
              section.classList.remove('show');
            }
          });
        });
    
        contentSection.addEventListener('hide.bs.collapse', () => {
          toggleTriangle.style.borderBottom = 'none';
          toggleTriangle.style.borderTop = '8px solid white';
        });
      });

      netAmounts.forEach((netAmount, index) => {
        let checkboxes = contentSections[index].querySelectorAll('.btn-check');
      
        let fee = data[index]["Fee"]
        
        checkboxes.forEach(checkbox => {
          checkbox.addEventListener('click', function() {
            let checkedMonth = checkedMonths[index];
            
            if (checkbox.checked) {
              checkedMonth.textContent = parseInt(checkedMonth.textContent) + 1;
            } else {
              checkedMonth.textContent = parseInt(checkedMonth.textContent) - 1;
            }
    
            netAmount.value = parseInt(checkedMonth.textContent) * fee
            
            var sum=0
            netAmounts.forEach(net => {
              if (isNaN(parseInt(net.value))){return}
              sum = sum + parseInt(net.value)})
    
            grandTotal.textContent='₹'+sum
          });
        });
      });
  })
  
}

function Pay() {
  const verifycheck = document.getElementById('verifyCheckbox');

  if(!verifycheck.checked){
    showAlert(message="First, check the checkbox to confirm payment, then proceed to pay the fees.", type='danger', timeout=4000, element='modal-body 2')
    return}
  

  const contentSections = document.querySelectorAll('[id^="contentSection"]');
  contentSections.forEach((contentSection, index) => {

    var checked = contentSection.querySelectorAll('.btn-check:checked');
    var checkedValues = Array.from(checked).map(function(checkbox) {
        return checkbox.getAttribute("data-name");
    });

    fetch('/getfees', { // Replace with your server URL
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          studentId: sharedData[index].id, // Replace with actual ID
          months: checkedValues, // Replace with desired months
          task: 'update'
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.STATUS === "SUCCESS") {
        // If the status is SUCCESS, close the modal
        localStorage.setItem('reloadFlag', 'true');
        location.reload();
        }
      else {
        // If the status is FAILED, you can show an error message or leave the modal open
        showAlert(message="There is a problem, try again", type='danger', timeout=4000, element='modal-body')}
    })

  })
}

function verifyModal() {
  if (grandTotal.textContent.trim() === '₹0'){
    showAlert(message="You need to select a month in order to pay the fees.", type='danger', timeout=4000,element='modal-body'); return
  } else {
    // Hide Modal 1 and Show Modal 2
    bootstrap.Modal.getInstance(document.getElementById('feesModal')).hide();
    new bootstrap.Modal(document.getElementById('verify')).show();
  }
}


function showAlert(message, type, timeout, element) {
  const alertContainer = document.getElementsByClassName(element)[0];

  // Create the alert div
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show mb-1 mt-1`;
  alertDiv.role = 'alert';
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;

  // Append the alert to the container
  alertContainer.prepend(alertDiv);

  // Automatically remove the alert after the specified timeout
  setTimeout(() => {
    alertDiv.classList.remove('show'); // Start the fade-out effect
    alertDiv.classList.add('hide');
    setTimeout(() => alertDiv.remove(), 500); // Fully remove the element after fading out
  }, timeout);
}

if (localStorage.getItem('reloadFlag')) {
  showAlert('Fees Paid Successfully', 'success', 4000, element='container-xl mt-4');
  localStorage.removeItem('reloadFlag'); // Clear the flag after showing the alert
}
