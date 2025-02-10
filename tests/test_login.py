import unittest
from app import app

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_post_valid(self):
        response = self.app.post('/login', data=dict(username='testuser', password='Test@123'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_invalid_password(self):
        response = self.app.post('/login', data=dict(username='testuser', password='WrongPass'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password. Please try again.', response.data)

    def test_login_post_non_existent_user(self):
        response = self.app.post('/login', data=dict(username='nonexistent', password='Test@123'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password. Please try again.', response.data)

if __name__ == '__main__':
    unittest.main()
