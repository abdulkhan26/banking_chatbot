import re
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

# Store chat states to manage conversations
user_states = {}

def log_conversation(user_id, user_message, bot_response):
    """Logs user-bot interactions into a user-specific file with timestamps."""
    log_dir = "chat_logs"
    os.makedirs(log_dir, exist_ok=True)  # Ensure directory exists
    log_file = os.path.join(log_dir, f"{user_id}_conversation.log")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] User: {user_message}\n")
            f.write(f"[{timestamp}] Bot: {bot_response}\n\n")
    except Exception as e:
        print(f"Error logging conversation: {str(e)}")

def handle_chatbot_response(user_id, message):
    original_message = message  # Preserve original message for logging
    
    if user_id not in user_states:
        user_states[user_id] = {'state': 'initial'}

    state = user_states[user_id]['state']

    # Enhanced Logging
    print(f"User ID: {user_id}")
    print(f"Received message: {original_message}")

    # Initialize response early for empty message case
    response = "Sorry, I didn't catch that. Can you please type your message again?"

    if not original_message.strip():
        log_conversation(user_id, original_message, response)
        return response

    # Process message for internal logic
    processed_message = original_message.lower().strip()
    response = ""  # Reset response for normal flow

    # State machine logic using PROCESSED message
    if state == 'initial':
        if 'hello' in processed_message:
            response = "Hello! How can I help you today? Options: balance, transaction history, debit, change pin, update details, loan details."
            user_states[user_id]['state'] = 'awaiting_command'
        else:
            response = "Please start the conversation by saying 'hello'."
    
    elif state == 'awaiting_command':
        if 'balance' in processed_message:
            balance = get_balance(user_id)
            response = f"Your current balance is Rs.{balance:.2f}"
        elif 'transaction history' in processed_message:
            history = get_transaction_history(user_id)
            response = format_transaction_history(history)
        elif 'debit' in processed_message:
            response = "Please enter the amount to debit and the recipient's account number (space-separated)."
            user_states[user_id]['state'] = 'awaiting_debit_details'
        elif 'change pin' in processed_message:
            response = "Please enter your current PIN."
            user_states[user_id]['state'] = 'awaiting_current_pin'
        elif 'update details' in processed_message:
            response = "Which details would you like to update? (email/username/phone_number)"
            user_states[user_id]['state'] = 'awaiting_detail_type'
        elif 'loan details' in processed_message:
            loan_amount = User.get_loan_amount(user_id)
            response = f"Your current loan amount is Rs.{loan_amount:.2f}"
        else:
            response = "I didn't understand that. Available commands: balance, transaction history, debit, change pin, update details, loan details."
    
    elif state == 'awaiting_debit_details':
        try:
            amount_str, recipient_account = processed_message.split()
            amount = float(amount_str)
            transaction_response = debit_account(user_id, amount, recipient_account)
            response = transaction_response
        except ValueError:
            response = "Invalid format. Please enter: AMOUNT ACCOUNT_NUMBER (e.g., '500 123456789')"
        finally:
            user_states[user_id]['state'] = 'awaiting_command'
    
    elif state == 'awaiting_current_pin':
        if User.verify_pin(user_id, processed_message):
            user_states[user_id]['current_pin'] = processed_message
            response = "Please enter your new PIN."
            user_states[user_id]['state'] = 'awaiting_new_pin'
        else:
            response = "❌ Incorrect PIN. Please try again."
    
    elif state == 'awaiting_new_pin':
        if 'current_pin' in user_states[user_id]:
            result = change_user_pin(
                user_id,
                user_states[user_id]['current_pin'],
                processed_message
            )
            response = result
            user_states[user_id] = {'state': 'awaiting_command'}  # Full reset
        else:
            response = "⚠️ Session error. Please start over."
    
    elif state == 'awaiting_detail_type':
        allowed_details = ['email', 'username', 'phone_number']
        if processed_message in allowed_details:
            user_states[user_id]['detail_type'] = processed_message
            response = f"Enter new {processed_message}:"
            user_states[user_id]['state'] = 'awaiting_detail_value'
        else:
            response = f"Invalid option. Choose from: {', '.join(allowed_details)}"
    
    elif state == 'awaiting_detail_value':
        detail_type = user_states[user_id].get('detail_type')
        if detail_type:
            update_response = update_user_details(user_id, detail_type, original_message)  # Use original for case-sensitive values
            response = update_response
            user_states[user_id] = {'state': 'awaiting_command'}
        else:
            response = "⚠️ Session error. Please start over."

    # Log conversation before returning response
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