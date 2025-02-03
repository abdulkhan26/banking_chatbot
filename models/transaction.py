# transaction.py

from database import get_db_connection
import logging

class Transaction:
    @staticmethod
    def log_transaction(user_id, amount, transaction_type, recipient_account=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO transactions (user_id, amount, transaction_type, recipient_account)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount, transaction_type, recipient_account))
            conn.commit()
        except Exception as e:
            logging.error(f"Error logging transaction: {e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_transaction_history(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT amount, transaction_type, recipient_account, timestamp
            FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (user_id,))
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()
        return transactions
