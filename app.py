from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the SQLite Database (using all.db)
def init_sqlite_db():
    with sqlite3.connect('all.db') as con:
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            exam_results TEXT
        );
        ''')
        con.commit()

# Call the function to initialize the database
init_sqlite_db()

# Helper function to generate the study schedule
def generate_schedule(exam_results):
    schedule = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}
    total_hours_per_week = 20  # Total hours to distribute among subjects
    max_hours_per_day = 3  # Maximum hours of study per day
    weak_grades = ['F', 'D', 'E']  # Grades considered weak
    subjects = exam_results.keys()

    # Assign more time to weak subjects
    weak_subjects = {subject: grade for subject, grade in exam_results.items() if grade in weak_grades}
    non_weak_subjects = {subject: grade for subject, grade in exam_results.items() if grade not in weak_grades}

    # Determine hours per subject (longer for weak subjects)
    weak_hours = total_hours_per_week * 0.7  # 70% of time for weak subjects
    non_weak_hours = total_hours_per_week * 0.3  # 30% for stronger subjects

    if weak_subjects:
        hours_per_weak_subject = weak_hours / len(weak_subjects)
    else:
        hours_per_weak_subject = 0

    if non_weak_subjects:
        hours_per_non_weak_subject = non_weak_hours / len(non_weak_subjects)
    else:
        hours_per_non_weak_subject = 0

    # Distribute subjects across the days
    days = list(schedule.keys())
    day_index = 0

    # Helper function to add subjects to the schedule
    def add_to_schedule(subject, hours):
        nonlocal day_index
        hours_left = hours
        while hours_left > 0:
            available_hours = min(max_hours_per_day, hours_left)
            day_schedule = schedule[days[day_index]]
            
            # If there's room for another subject on the same day
            if len(day_schedule) < 2 and (day_schedule and available_hours <= 3 - sum(float(item.split(":")[1].split()[0]) for item in day_schedule)):
                day_schedule.append(f"{subject}: {round(available_hours, 2)} hours")
                hours_left -= available_hours
                day_index = (day_index + 1) % 7  # Move to the next day
            else:
                # Move to the next day if no room or it's the end of the day
                day_index = (day_index + 1) % 7
                if len(schedule[days[day_index]]) < 2:
                    day_schedule = schedule[days[day_index]]
                    day_schedule.append(f"{subject}: {round(available_hours, 2)} hours")
                    hours_left -= available_hours
                else:
                    day_index = (day_index + 1) % 7  # Continue to the next day

    # Assign hours for weak subjects
    for subject in weak_subjects:
        add_to_schedule(subject, hours_per_weak_subject)

    # Assign hours for non-weak subjects
    for subject in non_weak_subjects:
        add_to_schedule(subject, hours_per_non_weak_subject)

    return schedule



# Route for the home page
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# Route for the sign-up page
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        subjects = request.form.getlist('subjects[]')
        grades = request.form.getlist('grades[]')

        exam_results = dict(zip(subjects, grades))
        exam_results_json = json.dumps(exam_results)

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect('all.db') as con:
                cur = con.cursor()
                cur.execute('''INSERT INTO users (name, age, email, password, exam_results)
                               VALUES (?, ?, ?, ?, ?)''', 
                            (name, age, email, hashed_password, exam_results_json))
                con.commit()
                flash('Signup successful! Please log in.', 'success')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'danger')
        except Exception as e:
            flash(f'An error occurred during sign-up: {str(e)}', 'danger')

    return render_template('signup.html')

# Route for the login page
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('all.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

            if user:
                stored_hash = user[4]

                if check_password_hash(stored_hash, password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['name'] = user[1]
                    session['age'] = user[2]
                    session['email'] = user[3]
                    session['exam_results'] = user[5]
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Incorrect password!', 'danger')
            else:
                flash('Email not found!', 'danger')

    return render_template('login.html')

# Route for the user dashboard page
@app.route('/dashboard/')
def dashboard():
    if 'username' in session:
        exam_results = json.loads(session['exam_results'])
        return render_template('dashboard.html', 
                               name=session['name'], 
                               age=session['age'], 
                               email=session['email'], 
                               exam_results=exam_results)
    else:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login'))

# Route for the study schedule page
@app.route('/schedule/')
def schedule():
    if 'username' in session:
        exam_results = json.loads(session['exam_results'])
        study_schedule = generate_schedule(exam_results)
        return render_template('schedule.html', name=session['name'], schedule=study_schedule)
    else:
        flash('Please log in to view your study schedule.', 'danger')
        return redirect(url_for('login'))

# Route for logging out
@app.route('/logout/')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route for viewing the database (console output)
@app.route('/view_database/')
def view_database():
    with sqlite3.connect('all.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    return "Check your console for database entries."

if __name__ == '__main__':
    app.run(debug=True)
