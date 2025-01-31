import sqlite3

def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if they exist (for recreation)
    cursor.execute('DROP TABLE IF EXISTS transactions')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS loan_accounts')

    # Create users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        account_number TEXT NOT NULL UNIQUE,
        balance DECIMAL(15, 2) DEFAULT 0.00
    )
    ''')

    # Create transactions table
    cursor.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount DECIMAL(15, 2) NOT NULL,
        transaction_type TEXT CHECK(transaction_type IN ('debit', 'credit')) NOT NULL,
        recipient_account TEXT DEFAULT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create loan_accounts table
    cursor.execute('''
    CREATE TABLE loan_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        pin TEXT NOT NULL,
        account_number TEXT NOT NULL UNIQUE,
        loans DECIMAL(15, 2) DEFAULT 0.00
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    db_path = 'database.db'
    initialize_database(db_path)
