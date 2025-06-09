import unittest
from unittest.mock import Mock, patch
import torch
import sys
import os

# Add the parent directory to the path to import the Library module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Library.EmotionDetector import EmotionDetector


class TestPredictFunction(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the load_model function to avoid loading actual models
        self.mock_tokenizer = Mock()
        self.mock_model = Mock()

        self.mock_tokenizer.return_value = {
            "input_ids": torch.tensor([[101, 1045, 2293, 2023, 102]]),
            "attention_mask": torch.tensor([[1, 1, 1, 1, 1]]),
        }

        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[0.1, 0.8, 0.2, 0.1, 0.1, 0.3]])
        self.mock_model.return_value = mock_outputs
        self.mock_model.to = Mock()

        with patch("Library.EmotionDetector.load_model") as mock_load:
            mock_load.return_value = (self.mock_tokenizer, self.mock_model)
            self.detector = EmotionDetector("fake_model_path", use_cuda=False)

    def test_predict_returns_correct_format(self):
        """Test that predict returns the expected tuple format."""
        text = "I am happy"
        result = self.detector.predict(text)

        # Should return tuple of (preprocessed_text, predicted_label, probability)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

        preprocessed_text, predicted_label, probability = result
        self.assertIsInstance(preprocessed_text, str)
        self.assertIsInstance(predicted_label, str)
        self.assertIsInstance(probability, float)

    def test_predict_with_simple_text(self):
        """Test predict function with simple text input."""
        text = "I am very happy today!"

        preprocessed_text, predicted_label, probability = self.detector.predict(text)

        # Check preprocessed text (should be lowercase, no special chars)
        self.assertEqual(preprocessed_text, "i am very happy today")

        # Check predicted label is valid emotion
        valid_emotions = ["sadness", "joy", "love", "anger", "fear", "surprise"]
        self.assertIn(predicted_label, valid_emotions)

        # Check probability is between 0 and 1
        self.assertGreater(probability, 0)
        self.assertLessEqual(probability, 1)

    def test_predict_selects_highest_logit(self):
        """Test that predict selects the emotion with highest logit score."""
        text = "Test text"

        # Mock model to return specific logits where index 1 (joy) is highest
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[0.1, 0.9, 0.2, 0.1, 0.1, 0.1]])
        self.mock_model.return_value = mock_outputs

        _, predicted_label, _ = self.detector.predict(text)

        # Should predict "joy" since it has highest logit (index 1)
        self.assertEqual(predicted_label, "joy")

    def test_predict_with_different_emotions(self):
        """Test predict with logits favoring different emotions."""
        text = "Test text"

        # Test each emotion
        emotions_to_test = {
            0: "sadness",
            1: "joy",
            2: "love",
            3: "anger",
            4: "fear",
            5: "surprise",
        }

        for emotion_id, emotion_name in emotions_to_test.items():
            # Create logits where this emotion has highest score
            logits = [0.1] * 6
            logits[emotion_id] = 0.8

            mock_outputs = Mock()
            mock_outputs.logits = torch.tensor([logits])
            self.mock_model.return_value = mock_outputs

            _, predicted_label, _ = self.detector.predict(text)
            self.assertEqual(predicted_label, emotion_name)

    def test_predict_probability_calculation(self):
        """Test that probability is calculated correctly."""
        text = "Test text"

        # Set known logits for probability calculation
        logits = torch.tensor([[1.0, 2.0, 0.5, 0.1, 0.3, 0.8]])
        mock_outputs = Mock()
        mock_outputs.logits = logits
        self.mock_model.return_value = mock_outputs

        _, predicted_label, probability = self.detector.predict(text)

        # Highest logit is at index 1 (value 2.0) = "joy"
        self.assertEqual(predicted_label, "joy")

        # Probability should be reasonable (softmax of highest value)
        self.assertEqual(round(probability, 3), 0.45)
        self.assertLess(probability, 1.0)

    def test_predict_with_empty_text(self):
        """Test predict function with empty text."""
        text = ""

        result = self.detector.predict(text)

        # Should still return valid format even with empty text
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

        preprocessed_text, predicted_label, probability = result
        self.assertEqual(preprocessed_text, "")
        self.assertIn(
            predicted_label, ["sadness", "joy", "love", "anger", "fear", "surprise"]
        )
        self.assertIsInstance(probability, float)


if __name__ == "__main__":
    unittest.main()
