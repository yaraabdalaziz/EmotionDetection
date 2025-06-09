import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Database.UsersRepo import UsersRepo


class TestUsersRepo(unittest.TestCase):

    def setUp(self):
        self.users_repo = UsersRepo()

    @patch("Database.UsersRepo.get_connection")
    @patch("Database.UsersRepo.encrypt_password")
    @patch("Database.UsersRepo.generate_api_key")
    def test_add_new_user_success(
        self, mock_generate_api_key, mock_encrypt_password, mock_get_connection
    ):
        """Test successful addition of a new user."""
        # Mock the helper functions
        mock_encrypt_password.return_value = "hashed_password_123"
        mock_generate_api_key.return_value = "api_key_abc123"

        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        email = "test@example.com"
        password = "password123"
        quota = 50

        # Call the method
        result = self.users_repo.add_new_user(email, password, quota)

        # Verify the result
        self.assertEqual(result, "api_key_abc123")

        # Verify helper functions were called
        mock_encrypt_password.assert_called_once_with(password)
        mock_generate_api_key.assert_called_once()

        # Verify the correct SQL was executed
        expected_sql = """
                INSERT INTO users (email, password, api_key, quota, available_requests)
                VALUES (?, ?, ?, ?, ?)
            """
        mock_cursor.execute.assert_called_once_with(
            expected_sql, (email, "hashed_password_123", "api_key_abc123", quota, quota)
        )

        # Verify commit was called
        mock_conn.commit.assert_called_once()

    @patch("Database.UsersRepo.get_connection")
    def test_get_user_id_success(self, mock_get_connection):
        """Test successful retrieval of user ID by API key."""
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (123,)  # Return tuple with user_id
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        api_key = "valid_api_key_123"

        # Call the method
        result = self.users_repo.get_user_id(api_key)

        # Verify the result
        self.assertEqual(result, 123)

        # Verify the correct SQL was executed
        mock_cursor.execute.assert_called_once_with(
            "SELECT user_id FROM users WHERE api_key = ?", (api_key,)
        )

        # Verify fetchone was called
        mock_cursor.fetchone.assert_called_once()

    @patch("Database.UsersRepo.get_connection")
    def test_decrement_user_quota_success(self, mock_get_connection):
        """Test successful quota decrement."""
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simulate successful update
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        user_id = 456

        # Call the method
        result = self.users_repo.decrement_user_quota(user_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the transaction was started
        mock_conn.execute.assert_called_once_with("BEGIN IMMEDIATE")

        # Verify the correct SQL was executed
        expected_sql = """
                        UPDATE users 
                        SET available_requests = available_requests - 1 
                        WHERE user_id = ? AND available_requests > 0
                    """
        mock_cursor.execute.assert_called_once_with(expected_sql, (user_id,))

        # Verify commit was called
        mock_conn.commit.assert_called_once()

    @patch("Database.UsersRepo.get_connection")
    def test_increment_user_quota_success(self, mock_get_connection):
        """Test successful quota increment."""
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simulate successful update
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        user_id = 789

        # Call the method
        result = self.users_repo.incerement_user_quota(user_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the transaction was started
        mock_conn.execute.assert_called_once_with("BEGIN IMMEDIATE")

        # Verify the correct SQL was executed
        expected_sql = """
                        UPDATE users 
                        SET available_requests = available_requests + 1 
                        WHERE user_id = ? 
                    """
        mock_cursor.execute.assert_called_once_with(expected_sql, (user_id,))

        # Verify commit was called
        mock_conn.commit.assert_called_once()

    @patch("Database.UsersRepo.get_connection")
    def test_has_quota_success_with_quota(self, mock_get_connection):
        """Test successful check when user has quota available."""
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (25,)  # User has 25 requests remaining
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        user_id = 321

        # Call the method
        result = self.users_repo.has_quota(user_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the correct SQL was executed
        mock_cursor.execute.assert_called_once_with(
            "SELECT available_requests FROM users WHERE user_id = ?", (user_id,)
        )

        # Verify fetchone was called
        mock_cursor.fetchone.assert_called_once()

    @patch("Database.UsersRepo.get_connection")
    def test_has_quota_success_no_quota(self, mock_get_connection):
        """Test successful check when user has no quota available."""
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)  # User has 0 requests remaining
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        user_id = 654

        # Call the method
        result = self.users_repo.has_quota(user_id)

        # Verify the result
        self.assertFalse(result)

        # Verify the correct SQL was executed
        mock_cursor.execute.assert_called_once_with(
            "SELECT available_requests FROM users WHERE user_id = ?", (user_id,)
        )

        # Verify fetchone was called
        mock_cursor.fetchone.assert_called_once()


if __name__ == "__main__":
    unittest.main()
