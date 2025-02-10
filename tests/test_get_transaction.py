import pytest
from models.transaction import Transaction

def test_get_transaction_history():
    transactions = Transaction.get_transaction_history(1)  # Assuming user ID 1 exists in the database
    assert type(transactions) == list
    assert len(transactions) <= 10  # Ensure it doesn't return more than 10 transactions

def test_get_transaction_history_no_transactions():
    transactions = Transaction.get_transaction_history(9999)  # Assuming user ID 9999 does not exist or has no transactions
    assert transactions == []

def test_get_transaction_history_invalid_user():
    transactions = Transaction.get_transaction_history(-1)  # Invalid user ID
    assert transactions == []
