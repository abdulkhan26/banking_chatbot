# banking_controller.py

from database import get_db_connection
from models.user import User
from models.transaction import Transaction
import logging
import sqlite3  # Import sqlite3 for exception handling

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_balance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.00

def get_transaction_history(user_id):
    return Transaction.get_transaction_history(user_id)

def debit_account(user_id, amount, recipient_account):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if recipient exists
        cursor.execute('SELECT id FROM users WHERE account_number = ?', (recipient_account,))
        recipient = cursor.fetchone()
        if not recipient:
            logging.error(f"Recipient account {recipient_account} not found.")
            return "Invalid recipient account number."

        recipient_id = recipient[0]
        
        # Check if user has sufficient balance
        cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        balance_row = cursor.fetchone()
        if not balance_row:
            logging.error(f"User ID {user_id} not found.")
            return "User not found."
        balance = balance_row[0]

        if balance < amount:
            logging.error(f"User ID {user_id} has insufficient funds. Balance: {balance}, Attempted Debit: {amount}")
            return "Insufficient funds."

        # Proceed with transaction
        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient_id))
        Transaction.log_transaction(user_id, -amount, 'debit', recipient_account)
        Transaction.log_transaction(recipient_id, amount, 'credit', recipient_account=None)
        conn.commit()
        logging.info(f"Debit transaction successful for user ID {user_id}, amount: {amount}, to recipient: {recipient_account}")
        return "Debit transaction successful."
    except Exception as e:
        conn.rollback()
        logging.error(f"Transaction failed: {str(e)}")
        return f"Transaction failed: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def credit_account(user_id, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
        Transaction.log_transaction(user_id, amount, 'credit')
        conn.commit()
        return "Credit transaction successful."
    except Exception as e:
        conn.rollback()
        return f"Transaction failed: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def change_user_pin(user_id, old_pin, new_pin):
    """
    Changes the user's PIN after verifying the old PIN.
    """
    result = User.change_pin(user_id, old_pin, new_pin)
    if result == "PIN changed successfully.":
        logging.info(f"PIN changed successfully for user ID {user_id}.")
        return result
    else:
        logging.error(f"Failed to change PIN for user ID {user_id}.")
        return result

def update_user_details(user_id, detail_type, new_value):
    field_mapping = {
        'email': 'email',
        'username': 'username',
        'phone_number': 'phone_number'
    }
    field = field_mapping.get(detail_type)
    if not field:
        logging.error(f"Invalid detail type provided: {detail_type}")
        return "Invalid detail type."

    logging.debug(f"Attempting to update {field} for user ID {user_id} with new value: {new_value}")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f'UPDATE users SET {field} = ? WHERE id = ?'
        cursor.execute(query, (new_value, user_id))
        conn.commit()
        logging.info(f"{field.replace('_', ' ').capitalize()} updated successfully for user ID {user_id}.")
        return f"{field.replace('_', ' ').capitalize()} updated successfully."
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"SQLite3 error during update of {field} for user ID {user_id}: {e}")
        return f"Database error occurred while updating {field}."
    except Exception as e:
        conn.rollback()
        logging.error(f"Unexpected error during update of {field} for user ID {user_id}: {e}")
        return f"An unexpected error occurred while updating {field}."
    finally:
        cursor.close()
        conn.close()
