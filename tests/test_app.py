import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from flask import Flask, g
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, detector


class TestDetectEmotionEndpoint(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Mock the detector service
        self.detector_patcher = patch("app.detector")
        self.mock_detector = self.detector_patcher.start()

        # Mock the auth service methods directly
        self.auth_service_patcher = patch("Services.AuthService.auth.authenticate_user")
        self.quota_service_patcher = patch("Services.AuthService.auth.consume_quota")
        self.return_quota_patcher = patch("Services.AuthService.auth.return_qouta")

        self.mock_auth_service = self.auth_service_patcher.start()
        self.mock_quota_service = self.quota_service_patcher.start()
        self.mock_return_quota = self.return_quota_patcher.start()
        # Configure auth service mocks to return valid responses
        self.mock_auth_service.return_value = "test_user_123"
        self.mock_quota_service.return_value = True
        self.mock_return_quota.return_value = True

    def tearDown(self):
        """Clean up after each test."""
        self.detector_patcher.stop()
        self.auth_service_patcher.stop()
        self.quota_service_patcher.stop()
        self.return_quota_patcher.stop()

    def test_detect_emotion_success(self):
        """Test successful emotion detection."""
        # Mock the detector response
        self.mock_detector.detect_emotion.return_value = (
            "i am very happy today",
            "joy",
            0.85,
        )

        # Test data
        test_data = {"text": "I am very happy today!"}

        # Make request with API key header
        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
            headers={"api-key": "test_api_key"},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)
        self.assertIn("preprocessed_text", response_data)
        self.assertIn("label", response_data)
        self.assertIn("probability", response_data)

        self.assertEqual(response_data["preprocessed_text"], "i am very happy today")
        self.assertEqual(response_data["label"], "joy")
        self.assertEqual(response_data["probability"], 0.85)

        # Verify detector was called with correct parameters
        self.mock_detector.detect_emotion.assert_called_once_with(
            "I am very happy today!", "test_user_123"
        )

    def test_detect_emotion_missing_text(self):
        """Test request with missing 'text' field."""
        test_data = {"message": "I am happy"}

        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
            headers={"api-key": "test_api_key"},
        )

        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Missing 'text' in request body")

    def test_detect_emotion_empty_request_body(self):
        """Test request with empty body."""
        response = self.client.post(
            "/detect-emotion",
            data="",
            content_type="application/json",
            headers={"api-key": "test_api_key"},
        )

        # Flask returns 400 for malformed JSON, which is expected
        self.assertEqual(response.status_code, 400)

        # Flask returns HTML error page for malformed JSON, not our JSON error
        # This is expected behavior for completely empty/invalid JSON
        self.assertIn(b"Bad Request", response.data)

    def test_detect_emotion_detector_exception(self):
        """Test handling of detector service exceptions."""
        # Mock detector to raise an exception
        self.mock_detector.detect_emotion.side_effect = Exception(
            "Model loading failed"
        )

        test_data = {"text": "I am happy"}

        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
            headers={"api-key": "test_api_key"},
        )

        self.assertEqual(response.status_code, 500)

        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Model loading failed")

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "healthy")

    def test_missing_api_key(self):
        """Test request without API key."""
        test_data = {"text": "I am happy"}

        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Missing API key")

    def test_invalid_api_key(self):
        """Test request with invalid API key."""
        # Mock auth service to return None for invalid key
        self.mock_auth_service.return_value = None

        test_data = {"text": "I am happy"}

        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
            headers={"api-key": "invalid_key"},
        )

        self.assertEqual(response.status_code, 401)

        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Invalid API key")

    def test_quota_exceeded(self):
        """Test request when quota is exceeded."""
        # Mock quota service to return False (quota exceeded)
        self.mock_quota_service.return_value = False

        test_data = {"text": "I am happy"}

        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
            headers={"api-key": "test_api_key"},
        )

        self.assertEqual(response.status_code, 429)

        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"]["code"], "quota_exceeded")


class TestDetectEmotionEndpointIntegration(unittest.TestCase):
    """Integration tests that test the actual decorators behavior."""

    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Mock only the detector service, not the auth decorators
        self.detector_patcher = patch("app.detector")
        self.mock_detector = self.detector_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.detector_patcher.stop()

    @patch("Services.AuthService.auth.authenticate_user")
    @patch("Services.AuthService.auth.consume_quota")
    def test_detect_emotion_with_auth_and_quota(
        self, mock_consume_quota, mock_authenticate
    ):
        """Test endpoint with actual auth and quota decorators."""
        # Mock auth service responses
        mock_authenticate.return_value = "test_user_123"
        mock_consume_quota.return_value = True

        # Mock detector response
        self.mock_detector.detect_emotion.return_value = ("i am happy", "joy", 0.85)

        test_data = {"text": "I am happy"}

        response = self.client.post(
            "/detect-emotion",
            data=json.dumps(test_data),
            content_type="application/json",
            headers={"api-key": "valid_api_key"},
        )

        self.assertEqual(response.status_code, 200)

        # Verify auth methods were called
        mock_authenticate.assert_called_once_with("valid_api_key")
        mock_consume_quota.assert_called_once_with("test_user_123")


if __name__ == "__main__":
    unittest.main()
