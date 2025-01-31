import sqlite3
import random
import time

DB_PATH = 'database.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def insert_users():
    """Inserts 10 users into the users table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    users = [
        ('user1@example.com', 'user1', 'pass123', '1000001', 5000.00),
        ('user2@example.com', 'user2', 'pass123', '1000002', 7500.50),
        ('user3@example.com', 'user3', 'pass123', '1000003', 6200.75),
        ('user4@example.com', 'user4', 'pass123', '1000004', 4800.00),
        ('user5@example.com', 'user5', 'pass123', '1000005', 3900.25),
        ('user6@example.com', 'user6', 'pass123', '1000006', 8100.00),
        ('user7@example.com', 'user7', 'pass123', '1000007', 9200.75),
        ('user8@example.com', 'user8', 'pass123', '1000008', 5600.25),
        ('user9@example.com', 'user9', 'pass123', '1000009', 7000.00),
        ('user10@example.com', 'user10', 'pass123', '1000010', 6500.50),
    ]

    cursor.executemany('''
        INSERT INTO users (email, username, password, account_number, balance)
        VALUES (?, ?, ?, ?, ?)
    ''', users)

    conn.commit()
    conn.close()
    print("Users inserted successfully.")

def insert_loans():
    """Inserts 10 loan accounts into the loan_accounts table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    loans = [
        ('User One', '1234', '1000001', 2000.00),
        ('User Two', '5678', '1000002', 1500.50),
        ('User Three', '9101', '1000003', 3200.75),
        ('User Four', '1121', '1000004', 1800.00),
        ('User Five', '3141', '1000005', 2900.25),
        ('User Six', '5161', '1000006', 7100.00),
        ('User Seven', '7181', '1000007', 6200.75),
        ('User Eight', '9201', '1000008', 2600.25),
        ('User Nine', '1222', '1000009', 4000.00),
        ('User Ten', '3242', '1000010', 3500.50),
    ]

    cursor.executemany('''
        INSERT INTO loan_accounts (name, pin, account_number, loans)
        VALUES (?, ?, ?, ?)
    ''', loans)

    conn.commit()
    conn.close()
    print("Loan accounts inserted successfully.")

def insert_transactions():
    """Generates random transactions for each user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    transaction_types = ['debit', 'credit']
    transactions = []

    for i in range(1, 11):  # 10 users
        for _ in range(3):  # Each user gets 3 transactions
            amount = round(random.uniform(50, 1000), 2)
            transaction_type = random.choice(transaction_types)
            recipient_account = f'10000{random.randint(1, 10)}' if transaction_type == 'debit' else None
            transactions.append((i, amount, transaction_type, recipient_account))

            # Simulate time delay to vary timestamps
            time.sleep(0.1)

    cursor.executemany('''
        INSERT INTO transactions (user_id, amount, transaction_type, recipient_account)
        VALUES (?, ?, ?, ?)
    ''', transactions)

    conn.commit()
    conn.close()
    print("Transactions inserted successfully.")

if __name__ == "__main__":
    insert_users()
    insert_loans()
    insert_transactions()
