#chatbot_controller.py
import os
import datetime
from controllers.banking_controller import (
    get_balance,
    get_transaction_history,
    debit_account,
    change_user_pin,
    update_user_details
)
from models.user import User
from models.loan_account import LoanAccount
import logging
from flask import session  # Use session for state management
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)

COMMAND_MAP = {
    '1': 'balance',
    '2': 'transaction history',
    '3': 'Send money',
    '4': 'change pin',
    '5': 'update details',
    '6': 'loan eligibility'
}

def format_options():
    """Helper function to format available options with numbers"""
    options = []
    for num, cmd in COMMAND_MAP.items():
        formatted_name = ' '.join([word.capitalize() for word in cmd.split()])
        options.append(f"{num}. {formatted_name}")
    return "\n".join(options)

def log_conversation(user_id, user_message, bot_response):
    """Logs user-bot interactions into a user-specific file with timestamps."""
    log_dir = "chat_logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{user_id}_conversation.log")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] User: {user_message}\n")
            f.write(f"[{timestamp}] Bot: {bot_response}\n\n")
    except Exception as e:
        logging.error(f"Error logging conversation: {str(e)}")

def is_valid_email(email):
    """Validate email using regex."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

def is_valid_username(username):
    """Validate username (starting with alphabets, followed by numbers, and minimum 4 characters)."""
    username_regex = r'^[a-zA-Z]{4,}\d+$'  # Must start with 4+ alphabets and end with digits
    return re.match(username_regex, username)

def handle_chatbot_response(user_id, message):
    
    original_message = message
    processed_message = original_message.lower().strip()

    if 'state' not in session:
        session['state'] = 'initial'

    state = session['state']
    response = "Sorry, I didn't catch that. Can you please type your message again?"

    logging.debug(f"User ID: {user_id}, State: {state}, Message: {original_message}")

    if processed_message == "exit":  # Check for exit command
        session['state'] = 'awaiting_command'
        response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        log_conversation(user_id, original_message, response)
        return response

    if not processed_message:
        log_conversation(user_id, original_message, response)
        return response

    # State machine logic
    if state == 'initial':
        if any(greeting in processed_message for greeting in ['hello', 'hi', 'hey']):
            response = f"Hello! How can I help you today? Please choose an option:\n{format_options()}"
            session['state'] = 'awaiting_command'
        else:
            response = "Please start the conversation by saying 'hi'."
    
    elif state == 'awaiting_command':
        selected_command = None
        
        if processed_message in COMMAND_MAP:
            selected_command = COMMAND_MAP[processed_message]
        else:
            for cmd in COMMAND_MAP.values():
                if cmd in processed_message:
                    selected_command = cmd
                    break

        logging.debug(f"Selected command: {selected_command}")

        if selected_command:
            if selected_command == 'balance':
                balance = get_balance(user_id)
                response = f"Your current balance is Rs.{balance:.2f}\n\nPlease choose an option:\n{format_options()}"
            elif selected_command == 'transaction history':
                history = get_transaction_history(user_id)
                response = format_transaction_history(history)+ f"\n\nDetailed History is sent to your mail" + f"\n\nPlease choose an option:\n{format_options()}"
            elif selected_command == 'Send money':
                response = "Please enter the amount to debit.\nPress X to exit."
                session['state'] = 'awaiting_debit_amount'  # Transition to awaiting amount
            elif selected_command == 'change pin':
                response = "Please enter your current PIN.\nPress X to exit."
                session['state'] = 'awaiting_current_pin'
            elif selected_command == 'update details':
                response = "Which details would you like to update? (email/username)\nPress X to exit."
                session['state'] = 'awaiting_detail_type'
            elif selected_command == "loan eligibility":
                response = "Please select your employment status:\n1️⃣ Employed\n2️⃣ Self-Employed\nPress X to exit."
                session['state'] = 'awaiting_employment_status'

        else:
            response = f"I didn't understand that. Please choose an option:\n{format_options()}"

    elif state == 'awaiting_debit_amount':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            try:
                amount = float(processed_message)
                
                # Check if the amount is positive
                if amount > 0:
                    session['debit_amount'] = amount  # Store the amount
                    response = "Please enter the recipient's account number.\nPress X to exit."
                    session['state'] = 'awaiting_debit_account'  # Transition to awaiting account number
                else:
                    response = "Please enter a valid positive amount.\nPress X to exit."
                    session['state'] = 'awaiting_debit_amount'
            except ValueError:
                response = "Invalid amount. Please enter a valid positive number.\nPress X to exit."


    elif state == 'awaiting_debit_account':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            recipient_account = processed_message
            amount = session.get('debit_amount')

            if not amount:
                response = "Please enter the amount first.\nPress X to exit."
                session['state'] = 'awaiting_debit_amount'
            else:
                # Proceed with the debit transaction
                transaction_response = debit_account(user_id, amount, recipient_account)
                response = transaction_response
                session.pop('debit_amount', None)
                session['state'] = 'awaiting_command'  # Reset to awaiting command state
                response += f"\n\nPlease choose an option:\n{format_options()}"

    elif state == 'awaiting_current_pin':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            if User.verify_pin(user_id, processed_message):
                session['current_pin'] = processed_message
                response = "Please enter your new PIN.\nPress X to exit."
                session['state'] = 'awaiting_new_pin'
            else:
                response = "❌ Incorrect PIN. Please try again.\nPress X to exit."
    
    elif state == 'awaiting_new_pin':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            if 'current_pin' in session:
                result = change_user_pin(
                    user_id,
                    session['current_pin'],
                    processed_message
                )
                response = result
                session.pop('current_pin', None)
                session['state'] = 'awaiting_command'
                response += f"\n\nPlease choose an option:\n{format_options()}"
            else:
                response = "⚠️ Session error. Please start over.\nPress X to exit."
        

    elif state == 'awaiting_detail_type':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            allowed_details = ['email', 'username']
            if processed_message in allowed_details:
                session['detail_type'] = processed_message
                response = f"Enter new {processed_message}:\nPress X to exit."
                session['state'] = 'awaiting_detail_value'
            else:
                response = f"Invalid option. Choose from: {', '.join(allowed_details)}\nPress X to exit."

    elif state == 'awaiting_detail_value':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            detail_type = session.get('detail_type')
            if detail_type:
                new_value = original_message.strip()

                # Validate the new email or username
                if detail_type == 'email':
                    if is_valid_email(new_value):
                        logging.debug(f"Updating {detail_type} to {new_value} for user ID {user_id}")
                        update_response = update_user_details(user_id, detail_type, new_value)
                        response = update_response
                        session.pop('detail_type', None)
                        session['state'] = 'awaiting_command'
                        response += f"\n\nPlease choose an option:\n{format_options()}"
                    else:
                        response = "❌ Invalid email format. Please enter a valid email.\nPress X to exit."
                elif detail_type == 'username':
                    if is_valid_username(new_value):
                        logging.debug(f"Updating {detail_type} to {new_value} for user ID {user_id}")
                        update_response = update_user_details(user_id, detail_type, new_value)
                        response = update_response
                        session.pop('detail_type', None)
                        session['state'] = 'awaiting_command'
                        response += f"\n\nPlease choose an option:\n{format_options()}"
                    else:
                        response = "❌ Invalid username. It must start with alphabets, followed by numbers, and be at least 4 characters long.\nPress X to exit."
                else:
                    response = "⚠️ Invalid detail type. Please try again.\nPress X to exit."
            else:
                response = "⚠️ Session error. Please start over.\nPress X to exit."
                session['state'] = 'awaiting_command'

    elif state == 'awaiting_employment_status':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            logging.debug(f"Processed message for employment status: '{processed_message}'")  # Debug the message
    
            if processed_message == "1":
                session['employment_status'] = "employed"
                response = "You selected **Employed**. Please enter your **monthly salary**:\nPress X to exit."
                session['state'] = 'awaiting_income_info'
            elif processed_message == "2":
                session['employment_status'] = "self-employed"
                response = "You selected **Self-Employed**. Please enter your **annual business turnover**:\nPress X to exit."
                session['state'] = 'awaiting_income_info'
            else:
                response = "Invalid option. Please enter **1 for Employed** or **2 for Self-Employed**.\nPress X to exit."

    elif state == 'awaiting_income_info':
        if processed_message == 'x':
            session['state'] = 'awaiting_command'
            response = f"You have exited the current task. Please choose an option:\n{format_options()}"
        else:
            try:
                income = float(processed_message)
                status = session.pop('employment_status', None)

                if status:
                    loan_info = LoanAccount.determine_loan_eligibility(status, loan_type="Business Loan" if status == "self-employed" else "Personal Loan", salary=income if status == "employed" else None, business_turnover=income if status == "self-employed" else None)

                    if loan_info["status"] == "✅ Approved":
                        response = (
                            f"🏦 Loan Scheme: {loan_info['loan_type']}\n"
                            f"💰 Max Loan Amount: ₹{loan_info['loan_amount']:.2f}\n"
                            f"📉 Interest Rate: 10%\n"  # Example rate
                            f"📅 Repayment Tenure: 5 years"  # Example tenure
                        )
                    else:
                        response = loan_info["message"]
                session['state'] = 'awaiting_command'
                response += f"\n\nPlease choose an option:\n{format_options()}"
            except ValueError:
                response = "Invalid input. Please enter a valid number.\nPress X to exit."

    else:
        response = "Unexpected error. Returning to main menu.\nPress X to exit."
        session['state'] = 'awaiting_command'
        response += f"\n\nPlease choose an option:\n{format_options()}"
    
    log_conversation(user_id, original_message, response)
    return response



def format_transaction_history(transactions):
    if not transactions:
        return "No recent transactions found."
    
    formatted = ["Recent Transactions:"]
    for transaction in transactions:
        amount, transaction_type, recipient, timestamp = transaction
        formatted.append(
            f"{timestamp}: {transaction_type.capitalize()} Rs.{amount:.2f}"
            + (f" to {recipient}" if recipient else "")
        )
        
    return "\n".join(formatted) 
