import unittest
from app import app

class SignupTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_signup_post_valid(self):
        response = self.app.post('/signup', data=dict(email='valid@example.com', username='validuser', password='Valid@123', account_number='1234567'))
        self.assertEqual(response.status_code, 200)

    def test_signup_post_invalid_email(self):
        response = self.app.post('/signup', data=dict(email='invalidemail', username='validuser', password='Valid@123', account_number='1234567'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email format.', response.data)

    def test_signup_post_existing_email(self):
        response = self.app.post('/signup', data=dict(email='existing@example.com', username='newuser', password='NewUser@123', account_number='7654321'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email is already in use. Please use a different email.', response.data)

if __name__ == '__main__':
    unittest.main()
