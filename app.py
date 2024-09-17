from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Mapping grades to study hours per week
grade_hours_map = {
    "A": 1,  # 1 hour per week
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    subjects = data.get('subjects', [])
    
    total_hours = 0
    schedule = []
    
    for subject in subjects:
        subject_name = subject['name']
        grade = subject['grade']
        hours_per_week = grade_hours_map.get(grade, 0)  # Get hours based on grade
        total_hours += hours_per_week
        schedule.append({
            'subject': subject_name,
            'hours_per_week': hours_per_week
        })

    # Calculate the hourly study schedule (example: distribute hours evenly across the week)
    hours_per_day = math.ceil(total_hours / 7)
    
    # Create a schedule based on days of the week
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_schedule = {}
    for i, day in enumerate(days_of_week):
        day_schedule[day] = hours_per_day

    return jsonify({
        'schedule': day_schedule,
        'total_hours': total_hours
    })

if __name__ == '__main__':
    app.run(debug=True)
