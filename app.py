from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import os
import re
import random
import string
from datetime import datetime, timedelta
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

@app.route('/generate-otp', methods=['POST'])
def generate_otp():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and password == user['password']:
            # Generate 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            session['login_otp'] = otp
            session['temp_user_data'] = dict(user)
            return jsonify({'otp': otp})
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Error generating OTP'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user_otp = request.form.get('otp')

        if not user_otp:
            flash("Please generate and enter OTP")
            return render_template('login.html')

        stored_otp = session.get('login_otp')
        temp_user = session.get('temp_user_data')

        if not stored_otp or not temp_user:
            flash("Please generate OTP first")
            return render_template('login.html')

        if user_otp == stored_otp:
            session.clear()
            session['user_id'] = temp_user['id']
            session['username'] = temp_user['username']
            session['email'] = temp_user['email']
            session['state'] = 'initial'
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid OTP")
            return render_template('login.html')

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

@app.route('/logout',methods=['POST','GET'])
def logout():
    if 'user_id' in session:
        username = session.get('username')
        session.clear()
        flash(f"User '{username}' logged out successfully.")
    return redirect(url_for('login'))

@app.route('/services')
def services():
    return render_template('services.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/Q&A.txt')
def faq_file():
    return send_from_directory('.','Q&A.txt')

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal server error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
