import logging
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def verify_pin(user_id, input_pin):
    """
    Verifies the user's current PIN from the loan_accounts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch the PIN from the loan_accounts table
        cursor.execute('''
            SELECT pin FROM loan_accounts 
            WHERE account_number = (SELECT account_number FROM users WHERE id = ?)
        ''', (user_id,))
        result = cursor.fetchone()

        if result:
            stored_pin = result['pin']
            logging.debug(f"Stored PIN for user ID {user_id}: {stored_pin}")
            logging.debug(f"Input PIN: {input_pin}")

            if input_pin == stored_pin:
                logging.info(f"PIN verification successful for user ID {user_id} ✅")
                return True
            else:
                logging.warning(f"Incorrect PIN for user ID {user_id} ❌")
                return False
        else:
            logging.warning(f"No PIN found for user ID {user_id} ❌")
            return False
    except Exception as e:
        logging.error(f"Error verifying PIN for user ID {user_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def change_pin(user_id, new_pin):
    """
    Updates the user's PIN in the loan_accounts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Log the attempt to change the PIN
        logging.info(f"Attempting to change PIN for user ID {user_id} to {new_pin}")

        # Execute the update query
        cursor.execute('''
            UPDATE loan_accounts 
            SET pin = ? 
            WHERE account_number = (SELECT account_number FROM users WHERE id = ?)
        ''', (new_pin, user_id))

        # Check if the PIN was actually updated
        if cursor.rowcount > 0:
            conn.commit()
            logging.info(f"PIN changed successfully for user ID {user_id} ✅")
            return True
        else:
            logging.warning(f"No rows updated for user ID {user_id}. PIN may not exist or user ID is invalid.")
            return False
    except Exception as e:
        conn.rollback()
        logging.error(f"Error changing PIN for user ID {user_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def change_user_pin(user_id, old_pin, new_pin, confirm_pin):
    """
    Handles the process of changing the user's PIN.
    """
    # Validate that new PIN and confirm PIN match
    if new_pin != confirm_pin:
        logging.warning("New PIN and confirm PIN do not match.")
        return "New PIN and confirm PIN do not match."

    # Verify the old PIN
    if not verify_pin(user_id, old_pin):
        logging.warning("Invalid current PIN provided.")
        return "Invalid current PIN."

    # Attempt to change the PIN
    if change_pin(user_id, new_pin):
        logging.info(f"PIN changed successfully for user ID {user_id}.")
        return "PIN changed successfully."
    else:
        logging.error(f"Failed to change PIN for user ID {user_id}.")
        return "Failed to change PIN. Please try again."

# Example usage
if __name__ == "__main__":
    # Replace these values with actual user input or data
    user_id = 1  # Example user ID
    old_pin = "1234"  # Example current PIN
    new_pin = "4321"  # Example new PIN
    confirm_pin = "4321"  # Example confirm new PIN

    # Call the change_user_pin function
    result = change_user_pin(user_id, old_pin, new_pin, confirm_pin)
    print(result)  # Output the result