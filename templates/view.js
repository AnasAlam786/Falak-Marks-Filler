//JavaScript for search functionality

document.getElementById('search-input').addEventListener('keyup', function() {
    var filter = this.value.toLowerCase();
    var rows = document.getElementsByClassName('search-row');
    
    Array.from(rows).forEach(function(row) {
      var textContent = row.textContent.toLowerCase();
      if (textContent.includes(filter)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  });
