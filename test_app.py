import unittest
import sqlite3
from auth import create_connection, initialize_db, register_user, login_user

class TestPersonalFinanceApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create the database connection and initialize the database
        cls.conn = create_connection()
        initialize_db(cls.conn)

    def setUp(self):
        # Clear the users table before each test to avoid conflicts
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users")
        self.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close the database connection after all tests are done
        cls.conn.close()

    def test_register_user(self):
        # Test user registration
        response = register_user(self.conn, "testuser", "password123")
        self.assertEqual(response, "User registered successfully.")

    def test_login_user_success(self):
        # Test successful user login after registration
        register_user(self.conn, "testuser2", "password123")
        user = login_user(self.conn, "testuser2", "password123")
        self.assertIsNotNone(user)

    def test_login_user_failure(self):
        # Test login failure for non-existent user
        user = login_user(self.conn, "nonexistentuser", "password123")
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
