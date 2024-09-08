document.addEventListener('DOMContentLoaded', function () {
    function fetchFocusAreas() {
        fetch('/fetch_schedule')
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('.focus__table tbody');
                tbody.innerHTML = '';

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

    fetchFocusAreas();

    document.getElementById('results-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(this);

        fetch('/add_results', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(() => {
            fetchFocusAreas();
        })
        .catch(error => {
            console.error('Error submitting results:', error);
        });
    });

    document.getElementById('add-subject').addEventListener('click', function () {
        const subjectContainer = document.getElementById('subjects-container');
        const subjectCount = subjectContainer.children.length;

        if (subjectCount < 8) {
            const newSubjectDiv = document.createElement('div');
            newSubjectDiv.className = 'form-group';
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

