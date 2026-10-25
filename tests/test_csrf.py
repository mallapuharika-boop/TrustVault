
import unittest
from app import app

class CSRFTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = True
        self.client = app.test_client()

    def test_post_without_csrf_token_is_rejected(self):
        response = self.client.post(
            "/login",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
