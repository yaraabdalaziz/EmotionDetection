import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Database.HistoryRepo import HistoryRepo


class TestHistoryRepo(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.history_repo = HistoryRepo()

    @patch("Database.HistoryRepo.get_connection")
    def test_add_record_success(self, mock_get_connection):
        """Test successful addition of a record."""
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Test data
        input_text = "I am very happy today!"
        output_text = "joy"
        probability = 0.85
        user_id = 123

        # Call the method
        self.history_repo.add_record(input_text, output_text, probability, user_id)

        # Verify the connection was used as context manager
        mock_get_connection.assert_called_once()
        mock_get_connection.return_value.__enter__.assert_called_once()

        # Verify cursor was created and used
        mock_conn.cursor.assert_called_once()

        # Verify the correct SQL was executed with correct parameters
        expected_sql = """
                INSERT INTO requests_records (input, prediction, probability, user_id)
                VALUES (?, ?, ?, ?)
            """
        mock_cursor.execute.assert_called_once_with(
            expected_sql, (input_text, output_text, probability, user_id)
        )

        # Verify commit was called
        mock_conn.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
