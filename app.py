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

def generate_schedule(exam_results):
    schedule = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}
    max_hours_per_day = 3  # Maximum hours of study per day

    # Define study hours per grade
    grade_hours_mapping = {
        'A': 1.0,    
        'B': 1.5,    
        'C': 2.0,    
        'D': 2.5,  
        'E': 3.0,  
        'F': 3.5   
    }

    # Create a list of subjects with their respective study hours based on the grades
    subjects_with_hours = [(subject, grade_hours_mapping.get(grade, 1.0)) for subject, grade in exam_results.items()]

    # Assign subjects to each day, ensuring balance and maximum 2 subjects per day
    days = list(schedule.keys())
    day_index = 0

    for subject, hours in subjects_with_hours:
        while hours > 0:
            # Get the available hours for the current day
            available_hours = min(max_hours_per_day - sum(float(item.split(": ")[1].split()[0]) for item in schedule[days[day_index]]), hours)

            # If there's room for another subject on the current day
            if len(schedule[days[day_index]]) < 2 and available_hours > 0:
                schedule[days[day_index]].append(f"{subject}: {round(available_hours, 2)} hours")
                hours -= available_hours
            else:
                # Move to the next day
                day_index = (day_index + 1) % 7

    return schedule



# Route for the home page
@app.route('/')
def home():
        return render_template('STUDYSPHERE.html')


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

# Route for editing exam results
@app.route('/edit_exam_results/', methods=['GET', 'POST'])
def edit_exam_results():
    if 'username' in session:
        if request.method == 'POST':
            subjects = request.form.getlist('subjects[]')
            grades = request.form.getlist('grades[]')

            updated_exam_results = dict(zip(subjects, grades))
            updated_exam_results_json = json.dumps(updated_exam_results)
            user_id = session['user_id']
            with sqlite3.connect('all.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE users SET exam_results = ? WHERE id = ?", (updated_exam_results_json, user_id))
                con.commit()

            
            session['exam_results'] = updated_exam_results_json
            flash('Exam results updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        # Load current exam results to pre-fill the form
        exam_results = json.loads(session['exam_results'])
        return render_template('edit_exam_results.html', exam_results=exam_results)
    else:
        flash('Please log in to edit your exam results.', 'danger')
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
