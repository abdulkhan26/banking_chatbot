# loan_account.py

from database import get_db_connection
import logging

class LoanAccount:
    @staticmethod
    def create_loan_account(name, pin, account_number, loans):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO loan_accounts (name, pin, account_number, loans)
                VALUES (?, ?, ?, ?)
            ''', (name, pin, account_number, loans))
            conn.commit()
            logging.info(f"Loan account {account_number} created successfully ✅")
        except Exception as e:
            logging.error(f"Error creating loan account: {e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_loan_details(account_number):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM loan_accounts WHERE account_number = ?', (account_number,))
        loan_details = cursor.fetchone()
        cursor.close()
        conn.close()
        return loan_details
