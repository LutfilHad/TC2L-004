from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'subjects.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                grade TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                subject TEXT PRIMARY KEY,
                focus_level TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return render_template('')

@app.route('/schedule.html')
def schedule():
    return render_template('schedule.html')

@app.route('/add_results', methods=['POST'])
def add_results():
    try:
        form_data = request.form
        print(form_data)  # Log form data for debugging

        subjects = []
        for key, value in form_data.items():
            if key.startswith('subject') and value:
                index = key.replace('subject', '')
                grade_key = f'grade{index}'
                grade = form_data.get(grade_key)
                if grade:
                    subjects.append((value, grade))

        print(subjects)  # Log parsed subjects and grades for debugging

        if subjects:
            with get_db() as conn:
                conn.execute('DELETE FROM results')  # Clear previous results
                conn.executemany('''
                    INSERT INTO results (subject, grade)
                    VALUES (?, ?)
                ''', subjects)
                conn.commit()

                # Update focus areas based on the new results
                update_focus_areas()

        return 'Results submitted', 200
    except Exception as e:
        print(f"Error in add_results: {e}")
        return 'Error submitting results', 500

def grade_to_focus_level(grade):
    if grade in ['D', 'E', 'F']:
        return 'High'
    elif grade == 'C':
        return 'Medium'
    elif grade in ['A', 'B']:
        return 'Low'
    return 'None'

def update_focus_areas():
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM subjects')
            results = conn.execute('SELECT subject, grade FROM results').fetchall()

            for result in results:
                subject = result['subject']
                grade = result['grade']
                focus_level = grade_to_focus_level(grade)
                
                if focus_level != 'None':
                    conn.execute('''
                        INSERT OR REPLACE INTO subjects (subject, focus_level)
                        VALUES (?, ?)
                    ''', (subject, focus_level))
            conn.commit()

            # Log the updated focus areas
            updated_subjects = conn.execute('SELECT * FROM subjects').fetchall()
            print('Updated focus areas:', [dict(row) for row in updated_subjects])
    except Exception as e:
        print(f"Error in update_focus_areas: {e}")

@app.route('/generate_schedule', methods=['GET'])
def generate_schedule():
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT subject, focus_level FROM subjects')
            subjects = cursor.fetchall()

            schedule = []
            for subject in subjects:
                if subject['focus_level'] == 'High':
                    schedule.append(f"Study {subject['subject']} for 2 hours a day")
                elif subject['focus_level'] == 'Medium':
                    schedule.append(f"Study {subject['subject']} for 1 hour a day")
                elif subject['focus_level'] == 'Low':
                    schedule.append(f"Study {subject['subject']} for 30 minutes a day")

            # Log the generated schedule
            print('Generated schedule:', schedule)

            return jsonify(schedule)
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return jsonify([]), 500

@app.route('/progress.html')
def progress():
    return render_template('progress.html')

if __name__ == '__main__':
    app.run(debug=True)
