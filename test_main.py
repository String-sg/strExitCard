
"""Unit tests for the main application module."""

import unittest
from unittest.mock import patch, MagicMock
import main

class TestMainApp(unittest.TestCase):
    """Test cases for the main application functionality."""

    @patch('groq.Groq')
    def test_generate_questions(self, mock_groq):
        """Test the generate_questions function with mocked Groq client."""
        # Mock the Groq client response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test question"))]
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        # Test the generate_questions function
        result = main.generate_questions("test lesson")
        self.assertEqual(result, "Test question")

        # Verify Groq was called with correct parameters
        expected_msg = [
            {
                "role": "system",
                "content": "You are an enthusiastic, curious teacher assistant creating thought-provoking questions."
            },
            {
                "role": "user",
                "content": "Teacher: test lesson Can you create some engaging, "
                          "higher-order thinking questions related to this topic? Include interdisciplinary questions."
            }
        ]
        mock_groq.return_value.chat.completions.create.assert_called_with(
            model="llama-3.1-8b-instant",
            messages=expected_msg
        )

if __name__ == '__main__':
    unittest.main()
