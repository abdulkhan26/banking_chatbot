import pytest
from models.user import User

def test_change_pin_valid():
    result = User.change_pin(1, '1234', '5678')  # Assuming user ID 1 exists and old PIN is '1234'
    assert result == 'PIN changed successfully.'

def test_change_pin_invalid_current_pin():
    result = User.change_pin(1, 'wrongpin', '5678')
    assert result == 'Invalid current PIN.'

def test_change_pin_non_existent_user():
    result = User.change_pin(9999, '1234', '5678')
    assert result == 'Error changing PIN.'
