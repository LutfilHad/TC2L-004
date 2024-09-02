from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            username TEXT, 
            email TEXT UNIQUE, 
            password TEXT
        )
    ''')
    print("Table created successfully")
    conn.close()

init_sqlite_db()

@app.route('/')
def home():
    return render_template('STUDYSPHERE.html')

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])  # Hashing the password
            
            print(f"Generated hash: {password}")  # Debug: Print the generated hash
            
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                            (username, email, password))
                con.commit()
                flash("Record added successfully!", "success")
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
        except Exception as e:
            print(f"Exception: {e}")
            con.rollback()
            flash("Error in insert operation", "danger")
        
    return render_template('signup.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

            if user:
                print(f"User found: {user}")
                print(f"Entered password: '{password}'")  # Debug: Entered password
                print(f"Stored hash: {user[3]}")  # Debug: Stored hash

                if check_password_hash(user[3], password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
                else:
                    print("Password check failed")  # Debug: Password check failed
                    flash('Invalid credentials', 'danger')
            else:
                print("User not found")  # Debug: User not found
                flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/view_database/')
def view_database():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    return "Check your console for database entries."

if __name__ == '__main__':
    app.run(debug=True)

