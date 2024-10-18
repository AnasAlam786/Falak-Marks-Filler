document.addEventListener('DOMContentLoaded', function () {
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
});
