from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import os
import re  # Regular expressions for validation
from dotenv import load_dotenv
from controllers.chatbot_controller import handle_chatbot_response


# Load environment variables
load_dotenv()

# Flask App Setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Database Configuration
def get_db_connection():
    import sqlite3
    connection = sqlite3.connect(os.environ.get('SQLITE_DB'))
    connection.row_factory = sqlite3.Row
    return connection

# Regular expression patterns for validation
ACCOUNT_NUMBER_REGEX = r'^\d{12}$'  # Account number must be exactly 12 digits
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'  # Password requirements

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        account_number = request.form['account_number']
        
        # Regular expression validation for account number
        if not re.match(ACCOUNT_NUMBER_REGEX, account_number):
            error_message = "Account number must be exactly 12 digits."
            return render_template('signup.html', error=error_message)
        
        # Regular expression validation for password
        if not re.match(PASSWORD_REGEX, password):
            error_message = ("Password must be at least 8 characters long and include "
                             "uppercase letters, lowercase letters, numbers, and special characters.")
            return render_template('signup.html', error=error_message)
        
        # Connect to the database and insert user data
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Store the plain text password directly (not recommended)
            cursor.execute(
                "INSERT INTO users (email, username, password, account_number, balance) VALUES (?, ?, ?, ?, ?)",
                (email, username, password, account_number, 0.00)
            )
            connection.commit()
            cursor.close()
            connection.close()
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            connection.rollback()
            cursor.close()
            connection.close()
            error_message = f"Error creating account: {str(e)}"
            return render_template('signup.html', error=error_message)
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        print(f"User fetched from DB: {user}")  # Debug print

        if user and password == user['password']:
            session['user_id'] = user['id']
            session['username'] = username
            print(f"Session set for user: {username}")  # Debug print
            return redirect(url_for('dashboard'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error=error_message)

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    username = session['username']
    return render_template('dashboard.html', username=username)

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'response': 'User not logged in. Please log in first.'}), 401
    user_id = session.get('user_id')
    data = request.get_json()
    message = data.get('message')
    response = handle_chatbot_response(user_id, message)
    return jsonify({'response': response})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
