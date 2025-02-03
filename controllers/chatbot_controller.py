# chatbot_controller.py

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
import logging
from flask import session  # Use session for state management

# Configure logging
logging.basicConfig(level=logging.DEBUG)

COMMAND_MAP = {
    '1': 'balance',
    '2': 'transaction history',
    '3': 'debit',
    '4': 'change pin',
    '5': 'update details',
    '6': 'loan details'
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

def handle_chatbot_response(user_id, message):
    print("hello welcome")
    original_message = message
    processed_message = original_message.lower().strip()

    if 'state' not in session:
        session['state'] = 'initial'

    state = session['state']
    response = "Sorry, I didn't catch that. Can you please type your message again?"

    logging.debug(f"User ID: {user_id}, State: {state}, Message: {original_message}")

    if not processed_message:
        log_conversation(user_id, original_message, response)
        return response

    # State machine logic
    if state == 'initial':
        if 'hello' in processed_message:
            response = f"Hello! How can I help you today? Please choose an option:\n{format_options()}"
            session['state'] = 'awaiting_command'
        else:
            response = "Please start the conversation by saying 'hello'."
    
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
                response = f"Your current balance is Rs.{balance:.2f}"
            elif selected_command == 'transaction history':
                history = get_transaction_history(user_id)
                response = format_transaction_history(history)
            elif selected_command == 'debit':
                response = "Please enter the amount to debit."
                session['state'] = 'awaiting_debit_amount'  # Transition to awaiting amount
            elif selected_command == 'change pin':
                response = "Please enter your current PIN."
                session['state'] = 'awaiting_current_pin'
            elif selected_command == 'update details':
                response = "Which details would you like to update? (email/username/phone_number)"
                session['state'] = 'awaiting_detail_type'
            elif selected_command == 'loan details':
                loan_amount = User.get_loan_amount(user_id)
                response = f"Your current loan amount is Rs.{loan_amount:.2f}"
        else:
            response = f"I didn't understand that. Please choose an option:\n{format_options()}"

    elif state == 'awaiting_debit_amount':
        try:
            amount = float(processed_message)
            session['debit_amount'] = amount  # Store the amount
            response = "Please enter the recipient's account number."
            session['state'] = 'awaiting_debit_account'  # Transition to awaiting account number
        except ValueError:
            response = "Invalid amount. Please enter a valid number."

    elif state == 'awaiting_debit_account':
        recipient_account = processed_message
        amount = session.get('debit_amount')

        if not amount:
            response = "Please enter the amount first."
            session['state'] = 'awaiting_debit_amount'
        else:
            # Proceed with the debit transaction
            transaction_response = debit_account(user_id, amount, recipient_account)
            response = transaction_response
            session.pop('debit_amount', None)
            session['state'] = 'awaiting_command'  # Reset to awaiting command state

    elif state == 'awaiting_current_pin':
        if User.verify_pin(user_id, processed_message):
            session['current_pin'] = processed_message
            response = "Please enter your new PIN."
            session['state'] = 'awaiting_new_pin'
        else:
            response = "❌ Incorrect PIN. Please try again."
    
    elif state == 'awaiting_new_pin':
        if 'current_pin' in session:
            result = change_user_pin(
                user_id,
                session['current_pin'],
                processed_message
            )
            response = result
            session.pop('current_pin', None)
            session['state'] = 'awaiting_command'
        else:
            response = "⚠️ Session error. Please start over."

    elif state == 'awaiting_detail_type':
        allowed_details = ['email', 'username', 'phone_number']
        if processed_message in allowed_details:
            session['detail_type'] = processed_message
            response = f"Enter new {processed_message}:"
            session['state'] = 'awaiting_detail_value'
        else:
            response = f"Invalid option. Choose from: {', '.join(allowed_details)}"

    elif state == 'awaiting_detail_value':
        detail_type = session.get('detail_type')
        if detail_type:
            new_value = original_message.strip()
            logging.debug(f"Updating {detail_type} to {new_value} for user ID {user_id}")
            update_response = update_user_details(user_id, detail_type, new_value)
            response = update_response
            session.pop('detail_type', None)
            session['state'] = 'awaiting_command'
        else:
            response = "⚠️ Session error. Please start over."
            session['state'] = 'awaiting_command'

    else:
        response = "⚠️ Unexpected state. Returning to the main menu."
        session['state'] = 'awaiting_command'
        response += f"\n{format_options()}"

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
