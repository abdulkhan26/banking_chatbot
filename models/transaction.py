from database import get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Transaction:
    @staticmethod
    def log_transaction(user_id, amount, transaction_type, recipient_account=None):
        conn = get_db_connection()
        
        # Log connection status
        if not conn:
            logging.error("Failed to establish a database connection.")
            return
        
        cursor = conn.cursor()
        try:
            logging.debug(f"Inserting transaction: user_id={user_id}, amount={amount}, transaction_type={transaction_type}, recipient_account={recipient_account}")
            
            cursor.execute(''' 
                INSERT INTO transactions (user_id, amount, transaction_type, recipient_account)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount, transaction_type, recipient_account))
            
            # Commit the transaction
            conn.commit()
            logging.debug(f"Transaction successfully committed for user_id={user_id}.")
        
        except Exception as e:
            logging.error(f"Error logging transaction: {e}")
            conn.rollback()  # Rollback in case of error to maintain database integrity
        
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_transaction_history(user_id):
        conn = get_db_connection()
        
        # Log connection status
        if not conn:
            logging.error("Failed to establish a database connection.")
            return []

        cursor = conn.cursor()
        try:
            logging.debug(f"Fetching transaction history for user_id={user_id}")
            
            cursor.execute('''
                SELECT amount, transaction_type, recipient_account, timestamp
                FROM transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (user_id,))
            
            transactions = cursor.fetchall()
            logging.debug(f"Found {len(transactions)} transactions for user_id={user_id}.")
        
        except Exception as e:
            logging.error(f"Error fetching transaction history: {e}")
            transactions = []
        
        finally:
            cursor.close()
            conn.close()
        
        return transactions
