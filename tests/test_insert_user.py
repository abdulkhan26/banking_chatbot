import pytest
from models.user import User

def test_create_user():
    result = User.create_user('testuser@example.com', 'testuser', 'Test@123', '1234567')
    assert result == 'User created successfully.'

def test_create_user_duplicate_email():
    result = User.create_user('existing@example.com', 'newuser', 'NewUser@123', '7654321')
    assert result == 'Email is already in use. Please use a different email.'

def test_create_user_invalid_account_number():
    result = User.create_user('newuser@example.com', 'newuser', 'NewUser@123', 'invalid')
    assert result == 'Error creating user.'
