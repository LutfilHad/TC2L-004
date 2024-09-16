document.addEventListener('DOMContentLoaded', function () {
    // Fetch focus areas from the server
    function fetchFocusAreas() {
        fetch('/fetch_schedule')
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('.focus__table tbody');
                tbody.innerHTML = '';  // Clear previous table contents

                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="2">No subjects to focus on</td></tr>';
                } else {
                    data.forEach(subject => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${subject.subject}</td>
                            <td>${subject.focus_level}</td>
                        `;
                        tbody.appendChild(row);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching focus areas:', error);
            });
    }

    // Fetch study schedule from the server
    function fetchSchedule() {
        fetch('/generate_schedule')
            .then(response => response.json())
            .then(data => {
                const scheduleContainer = document.getElementById('schedule-container');
                scheduleContainer.innerHTML = '';  // Clear previous schedule

                if (data.length === 0) {
                    scheduleContainer.innerHTML = '<p>No schedule available.</p>';
                } else {
                    const ul = document.createElement('ul');
                    data.forEach(scheduleItem => {
                        const li = document.createElement('li');
                        li.textContent = scheduleItem;
                        ul.appendChild(li);
                    });
                    scheduleContainer.appendChild(ul);
                }
            })
            .catch(error => {
                console.error('Error generating schedule:', error);
            });
    }

    // Initial fetch when page loads
    fetchFocusAreas();

    // Handle form submission to submit results and update the UI
    document.getElementById('results-form').addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(this);  // Collect form data

        fetch('/add_results', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(() => {
            // Refresh the focus areas and schedule after successful submission
            fetchFocusAreas();
            fetchSchedule(); 
        })
        .catch(error => {
            console.error('Error submitting results:', error);
        });
    });

    // Handle the addition of more subjects (up to 8)
    document.getElementById('add-subject').addEventListener('click', function () {
        const subjectContainer = document.getElementById('subjects-container');
        const subjectCount = subjectContainer.querySelectorAll('.form-group').length;

        if (subjectCount < 8) {  // Limit to 8 subjects
            const newSubjectDiv = document.createElement('div');
            newSubjectDiv.className = 'form-group';  // Add form-group class for styling
            newSubjectDiv.innerHTML = `
                <label for="subject${subjectCount + 1}">Subject ${subjectCount + 1}:</label>
                <input type="text" id="subject${subjectCount + 1}" name="subject${subjectCount + 1}" required>
                <label for="grade${subjectCount + 1}">Grade:</label>
                <select id="grade${subjectCount + 1}" name="grade${subjectCount + 1}" required>
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
                    <option value="E">E</option>
                    <option value="F">F</option>
                </select>
            `;
            subjectContainer.appendChild(newSubjectDiv);
        }
    });
});
