from database import get_db_connection
from models.user import User
from models.transaction import Transaction
import logging
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
            return "Invalid account number."

        recipient_id = recipient[0]
        
        # Check if user has sufficient balance
        cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        balance_row = cursor.fetchone()
        if not balance_row:
            return "User not found."
        balance = balance_row[0]

        if balance < amount:
            return "Insufficient funds."

        # Proceed with transaction
        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient_id))
        Transaction.log_transaction(user_id, -amount, 'debit', recipient_account)
        Transaction.log_transaction(recipient_id, amount, 'credit')
        conn.commit()
        return "Debit transaction successful."
    except Exception as e:
        conn.rollback()
        return f"Transaction failed: {str(e)}"
    finally:
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
    allowed_details = ['email', 'username', 'phone_number']
    if detail_type not in allowed_details:
        return "Invalid detail type."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f'UPDATE users SET {detail_type} = ? WHERE id = ?'
        cursor.execute(query, (new_value, user_id))
        conn.commit()
        return f"{detail_type.capitalize()} updated successfully."
    except Exception as e:
        conn.rollback()
        return f"Failed to update {detail_type}: {str(e)}"
    finally:
        conn.close()
