
function openAddFromAdmissionsModal(courseId) {
  window.currentCourseId = courseId;
  document.getElementById('addFromAdmissionsModal').style.display = 'flex';
}

function closeAddFromAdmissionsModal() {
  document.getElementById('addFromAdmissionsModal').style.display = 'none';
  document.getElementById('admissionsSearchInput').value = '';
  document.getElementById('admissionsSearchResults').innerHTML = '<p style="text-align:center; color:#6B7280;">Enter a search term to find students</p>';
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getCSRFToken() {
  return window.csrfToken || getCookie('csrftoken');
}

function searchAdmittedStudents() {
  const query = document.getElementById('admissionsSearchInput').value.trim();
  if (!query) {
    alert('Please enter a search term');
    return;
  }

  const resultsDiv = document.getElementById('admissionsSearchResults');
  resultsDiv.innerHTML = '<p style="text-align:center; color:#6B7280;">Searching...</p>';

  fetch(`/registra/course/${window.currentCourseId}/search-admitted/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({ q: query })
  })
  .then(r => {
    // Handle non-JSON responses
    const contentType = r.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error(`Expected JSON response, got ${contentType || 'text/html'}`);
    }
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}: ${r.statusText}`);
    }
    return r.json();
  })
  .then(data => {
    if (data.error) {
      resultsDiv.innerHTML = '<p style="text-align:center; color:#DC2626; padding:1rem;">❌ ' + data.error + '</p>';
    } else if (data.students && data.students.length === 0) {
      resultsDiv.innerHTML = '<p style="text-align:center; color:#6B7280; padding:1rem;">No students found</p>';
    } else if (data.students) {
      resultsDiv.innerHTML = data.students.map(student => `
        <div class="modal-student-row">
          <div class="modal-student-info">
            <div class="modal-student-matricule">${student.matricule}</div>
            <div class="modal-student-name">${student.first_name} ${student.last_name}</div>
            <div class="modal-student-level">${student.level} • ${student.admitted_year}</div>
          </div>
          <button type="button" class="modal-add-btn" onclick="addStudentFromAdmissions('${student.matricule}')" ${student.already_enrolled ? 'disabled' : ''}>${student.already_enrolled ? 'Already Enrolled' : 'Add'}</button>
        </div>
      `).join('');
    }
  })
  .catch(err => {
    console.error('Search error:', err);
    resultsDiv.innerHTML = '<p style="text-align:center; color:#DC2626; padding:1rem;">❌ Error: ' + err.message + '</p>';
  });
}

function addStudentFromAdmissions(matricule) {
  fetch(`/registra/course/${window.currentCourseId}/add-admitted/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({ matricule: matricule })
  })
  .then(r => {
    const contentType = r.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error(`Expected JSON response, got ${contentType || 'text/html'}`);
    }
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}: ${r.statusText}`);
    }
    return r.json();
  })
  .then(data => {
    if (data.success) {
      alert('✅ ' + data.message);
      closeAddFromAdmissionsModal();
      location.reload();
    } else {
      alert('❌ ' + (data.error || 'Failed to add student'));
    }
  })
  .catch(err => {
    console.error('Add student error:', err);
    alert('❌ Error: ' + err.message);
  });
}

// Allow Enter key in search input
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('admissionsSearchInput');
  if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        searchAdmittedStudents();
      }
    });
  }
});
