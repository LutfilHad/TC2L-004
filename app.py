from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the SQLite Database (using all.db)
def init_sqlite_db():
    with sqlite3.connect('all.db') as con:  # Changed the database to all.db
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            exam_results TEXT NOT NULL  -- Stores JSON string of subjects and grades
        );
        ''')
        con.commit()

# Call the function to initialize the database
init_sqlite_db()

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
        subjects = request.form.getlist('subjects[]')  # Get the list of subjects
        grades = request.form.getlist('grades[]')      # Get the list of grades

        # Combine subjects and grades into a dictionary
        exam_results = dict(zip(subjects, grades))
        exam_results_json = json.dumps(exam_results)  # Convert to JSON to store in the database

        # Generate password hash
        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect('all.db') as con:  # Changed the database to all.db
                cur = con.cursor()
                cur.execute('''INSERT INTO users (name, age, email, password, exam_results)
                               VALUES (?, ?, ?, ?, ?)''', 
                            (name, age, email, hashed_password, exam_results_json))
                con.commit()
                flash('Signup successful! Please log in.', 'success')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'danger')
        except Exception:
            flash('An error occurred during sign-up.', 'danger')

    return render_template('signup.html')

# Route for the login page
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('all.db') as con:  # Changed the database to all.db
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

            if user:
                stored_hash = user[4]  # Password is in the 4th column

                if check_password_hash(stored_hash, password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]  # Username is user's name
                    session['name'] = user[1]      # Storing name in session
                    session['age'] = user[2]       # Storing age in session
                    session['email'] = user[3]     # Storing email in session
                    session['exam_results'] = user[5]  # Storing exam results in session
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
        exam_results = json.loads(session['exam_results'])  # Convert JSON back to dict
        return render_template('dashboard.html', 
                               name=session['name'], 
                               age=session['age'], 
                               email=session['email'],  # Display the actual email
                               exam_results=exam_results)
    else:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login'))

# Route for logging out
@app.route('/logout/')
def logout():
    session.clear()  # Clear the entire session at once
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
