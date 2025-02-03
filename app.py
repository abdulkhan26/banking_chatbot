from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import os
import re
import logging
import sqlite3
from dotenv import load_dotenv
from controllers.chatbot_controller import handle_chatbot_response
from controllers.banking_controller import (
    get_balance,
    get_transaction_history,
    debit_account,
    change_user_pin,
    update_user_details
)
from database import get_db_connection
from models.user import User
from flask import send_from_directory




# Load environment variables
load_dotenv()

# Flask App Setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Regular expression patterns for validation
ACCOUNT_NUMBER_REGEX = r'^\d{7}$'  # Account number must be exactly 7 digits
USERNAME_REGEX = r'^\w{3,20}$'      # Username criteria
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'  # Password requirements
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Simple email validation

# Logging Configuration
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        message = request.form['message'].strip()

        

        flash("Thank you for contacting us! We will get back to you soon.")
        return redirect(url_for('contact'))

    return render_template('contact.html')




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        account_number = request.form['account_number'].strip()

        errors = []

        # Validate email
        if not re.match(EMAIL_REGEX, email):
            errors.append("Invalid email format.")

        # Validate username
        if not re.match(USERNAME_REGEX, username):
            errors.append("Username must be 3-20 characters long and contain only letters, numbers, and underscores.")

        # Validate password
        if not re.match(PASSWORD_REGEX, password):
            errors.append("Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters.")

        # Validate account number
        if not re.match(ACCOUNT_NUMBER_REGEX, account_number):
            errors.append("Account number must be exactly 7 digits.")

        if errors:
            return render_template('signup.html', errors=errors)

        # Store user in database
        result = User.create_user(email, username, password, account_number)
        if result == "User created successfully.":
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))
        else:
            errors.append(result)
            return render_template('signup.html', errors=errors)
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        connection = get_db_connection()
        connection.row_factory = sqlite3.Row  # To access columns by name
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and password == user['password']:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']  # Store email for transaction notification
                session['state'] = 'initial'  # Initialize chatbot state
                logging.info(f"User '{username}' logged in successfully.")
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid username or password. Please try again."
                logging.warning(f"Failed login attempt for username: {username}")
                return render_template('login.html', error=error)
        except Exception as e:
            connection.rollback()
            logging.error(f"Error during login: {e}")
            error = "An error occurred during login. Please try again later."
            return render_template('login.html', error=error)
        finally:
            cursor.close()
            connection.close()
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('login'))
    username = session['username']
    return render_template('dashboard.html', username=username)

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'response': 'User not logged in. Please log in first.'}), 401
    user_id = session.get('user_id')
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'response': 'Welcome to DAV Bank! 😊 Please type "Hello" to start.'})
    message = data.get('message')
    response = handle_chatbot_response(user_id, message)
    return jsonify({'response': response.replace("\n", "<br>")})

@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    flash(f"User '{username}' logged out successfully.")
    return redirect(url_for('login'))

@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/Q&A.txt')
def faq_file():
    return send_from_directory('.', 'Q&A.txt')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal server error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
