# user.py

import logging
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class User:
    @staticmethod
    def create_user(email, username, password, account_number):
        """Creates a new user with a plain text password."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                logging.warning(f"Email {email} already exists. Cannot create user.")
                return "Email is already in use. Please use a different email."

            cursor.execute(''' 
                INSERT INTO users (email, username, password, account_number, balance)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, username, password, account_number, 0.00))
            conn.commit()
            logging.info(f"User {username} created successfully ✅")
            return "User created successfully."
        except Exception as e:
            conn.rollback()
            logging.error(f"Error creating user: {e}")
            return "Error creating user."
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def authenticate_user(username, password):
        """Authenticates a user by comparing plain text passwords."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                user_id, stored_password = result[0], result[1]
                if password == stored_password:
                    logging.info(f"User {username} authenticated successfully ✅")
                    return user_id
                else:
                    logging.warning(f"Incorrect password for user {username} ❌")
            else:
                logging.warning(f"User {username} not found ❌")
            return None
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def verify_pin(user_id, input_pin):
        """Verifies a user's PIN from the loan_accounts table."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(''' 
                SELECT pin FROM loan_accounts 
                WHERE account_number = (SELECT account_number FROM users WHERE id = ?)
            ''', (user_id,))
            result = cursor.fetchone()
            if result and input_pin == result[0]:
                logging.info(f"PIN verification successful for user ID {user_id} ✅")
                return True
            else:
                logging.warning(f"Incorrect PIN for user ID {user_id} ❌")
                return False
        except Exception as e:
            logging.error(f"Error verifying PIN: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def change_pin(user_id, old_pin, new_pin):
        """Changes the user's PIN after verifying the old PIN."""
        if not User.verify_pin(user_id, old_pin):
            logging.warning(f"Invalid current PIN for user ID {user_id}.")
            return "Invalid current PIN."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(''' 
                UPDATE loan_accounts 
                SET pin = ? 
                WHERE account_number = (SELECT account_number FROM users WHERE id = ?)
            ''', (new_pin, user_id))

            if cursor.rowcount > 0:
                conn.commit()
                logging.info(f"PIN changed successfully for user ID {user_id}.")
                return "PIN changed successfully."
            else:
                logging.warning(f"PIN change failed for user ID {user_id}. No matching record found.")
                return "PIN change failed."
        except Exception as e:
            conn.rollback()
            logging.error(f"Error changing PIN for user ID {user_id}: {e}")
            return "Error changing PIN."
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_loan_amount(user_id):
        """Gets the loan amount for a given user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(''' 
                SELECT loans FROM loan_accounts 
                WHERE account_number = (SELECT account_number FROM users WHERE id = ?)
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                loan_amount = result[0]
                logging.info(f"Loan amount for user ID {user_id}: Rs.{loan_amount:.2f}")
                return loan_amount
            else:
                logging.warning(f"No loan account found for user ID {user_id} ❌")
                return 0.00
        except Exception as e:
            logging.error(f"Error retrieving loan amount for user ID {user_id}: {e}")
            return 0.00
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_loan_amount(user_id, new_loan_amount):
        """Updates the loan amount for a given user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(''' 
                UPDATE loan_accounts 
                SET loans = ? 
                WHERE account_number = (SELECT account_number FROM users WHERE id = ?)
            ''', (new_loan_amount, user_id))

            if cursor.rowcount > 0:
                conn.commit()
                logging.info(f"Loan amount updated for user ID {user_id} ✅")
                return f"Loan amount updated to Rs.{new_loan_amount:.2f}."
            else:
                logging.warning(f"Loan update failed for user ID {user_id}. No matching record found ❌")
                return "Loan update failed."
        except Exception as e:
            conn.rollback()
            logging.error(f"Error updating loan amount for user ID {user_id}: {e}")
            return "Error updating loan amount."
        finally:
            cursor.close()
            conn.close()
