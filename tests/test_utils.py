# -*- coding: utf-8 -*-
"""Tests for utility functions."""

# Pre-register mock modules so @patch decorators don't import real deps
import sys
from unittest.mock import MagicMock

_MOCK_FILETYPE = MagicMock()
_MOCK_FILETYPE.guess.return_value = None
sys.modules.setdefault('filetype', _MOCK_FILETYPE)

_MOCK_GROQ = MagicMock()
sys.modules.setdefault('groq', _MOCK_GROQ)

# Import standard library modules for testing, mocking, file operations, and temp files
import unittest
from unittest.mock import patch
import os
import tempfile

# Use try/except to handle both installed and development environments
# Attempt to import the utils module from the package
try:
    # Import utils from the installed package
    from ai_image_renamer import utils
# Handle the case where the package is not installed
except ImportError:
    # Fallback for development/testing without installation
    # Import sys for path manipulation
    import sys
    # Add the src directory to the module search path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    # Import utils again after adjusting the path
    from ai_image_renamer import utils


# Define the test class for utility functions
class TestUtils(unittest.TestCase):
    """
    Unit tests for utility functions in the ai_image_renamer.utils module.

    These tests verify the core functionality of:
    - Image file validation (verify_image_file)
    - AI content generation (get_words)
    - Path sanitization (sanitize_image_path)
    - Image encoding (encode_image)

    All external dependencies (Groq API, filesystem) are mocked.
    """

    # Define a test method for verifying a valid image file
    @patch('filetype.guess', return_value=MagicMock(mime='image/jpeg'))
    def test_verify_image_file_with_valid_image(self, mock_guess):
        """
        Test that verify_image_file returns True for a valid image file.

        Uses a test image from the assets directory.
        """
        # Build the path to the test image in the assets directory
        test_image_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'test-image.jpg'
        )
        # Skip the test if the asset file does not exist
        if not os.path.exists(test_image_path):
            self.skipTest("Test image not found")
        # Call verify_image_file on the test image path
        result = utils.verify_image_file(test_image_path)
        # Assert that the result is True for a valid image
        self.assertTrue(result)

    # Define a test method for verifying a non-existent file
    def test_verify_image_file_with_nonexistent_file(self):
        """
        Test that verify_image_file returns False for non-existent file.

        The function should handle missing files gracefully without raising.
        """
        # Call verify_image_file with a non-existent path
        result = utils.verify_image_file('/nonexistent/path/image.jpg')
        # Assert that the result is False for a missing file
        self.assertFalse(result)

    # Define a test method for verifying a non-image file
    def test_verify_image_file_with_non_image_file(self):
        """
        Test that verify_image_file returns False for non-image files.

        Creates a temporary text file and verifies it's rejected.
        """
        # Create a temporary .txt file with non-image content
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            # Write non-image content to the temp file
            temp_file.write(b"This is not an image")
            # Store the temp file path
            temp_path = temp_file.name
        # Handle cleanup of temporary file
        try:
            # Call verify_image_file on the non-image file
            result = utils.verify_image_file(temp_path)
            # Assert that the result is False for non-image content
            self.assertFalse(result)
        # Ensure the temp file is deleted even if assertions fail
        finally:
            # Delete the temporary file
            os.unlink(temp_path)

    # Mock encode_image to return a fixed encoded string
    @patch('ai_image_renamer.utils.encode_image')
    # Mock filetype.guess to control MIME type detection
    @patch('filetype.guess')
    # Mock the Groq client to avoid real API calls
    @patch('groq.Groq')
    # Define a test method for a successful get_words call
    def test_get_words_success(self, mock_groq, mock_guess, mock_encode_image):
        """
        Test get_words function with a successful API call.

        Verifies that the function correctly extracts content from
        the Groq API response.
        """
        # Configure the mock to return a fixed encoded string
        mock_encode_image.return_value = "encoded_image_string"
        # Configure the mock to return a PNG MIME type
        mock_guess.return_value = MagicMock(mime='image/png')
        # Create a mock completion object
        mock_completion = MagicMock()
        # Set the expected content on the mock completion
        mock_completion.choices[0].message.content = "A test description"
        # Configure the Groq client mock to return the completion
        mock_groq.return_value.chat.completions.create.return_value = mock_completion
        # Call get_words with test parameters
        result = utils.get_words("test_image.jpg", words=8)
        # Assert that the result matches the mocked description
        self.assertEqual(result, "A test description")
        # Capture the kwargs passed to the Groq API create call
        create_kwargs = mock_groq.return_value.chat.completions.create.call_args.kwargs
        # Assert that the correct model name was used
        self.assertEqual(create_kwargs["model"], "meta-llama/llama-4-scout-17b-16e-instruct")
        # Assert that the vision URL includes the correct MIME type and encoded image
        self.assertEqual(
            create_kwargs["messages"][0]["content"][1]["image_url"]["url"],
            "data:image/png;base64,encoded_image_string",
        )

    # Mock encode_image to return a fixed encoded string
    @patch('ai_image_renamer.utils.encode_image')
    # Mock filetype.guess to control MIME type detection
    @patch('filetype.guess')
    # Mock the Groq client to avoid real API calls
    @patch('groq.Groq')
    # Define a test method for a failed get_words call
    def test_get_words_failure(self, mock_groq, mock_guess, mock_encode_image):
        """
        Test get_words function with a failed API call.

        Verifies that the function returns empty string when API fails.
        """
        # Configure the mock to return a fixed encoded string
        mock_encode_image.return_value = "encoded_image_string"
        # Configure the mock to return a JPEG MIME type
        mock_guess.return_value = MagicMock(mime='image/jpeg')
        # Configure Groq client mock to return a failed response (None)
        mock_groq.return_value.chat.completions.create.return_value = None
        # Call get_words with test parameters
        result = utils.get_words("test_image.jpg", words=8)
        # Assert that the result is an empty string on failure
        self.assertEqual(result, "")

    # Mock os.getenv to simulate missing environment variable
    @patch('ai_image_renamer.utils.os.getenv')
    # Define a test method for a missing API key scenario
    def test_get_words_missing_api_key(self, mock_getenv):
        """
        Test that get_words raises RuntimeError when API key is missing.
        """
        # Configure the mock to return None (no API key found)
        mock_getenv.return_value = None
        # Assert that calling get_words without an API key raises RuntimeError
        with self.assertRaises(RuntimeError):
            # Call get_words which should raise due to missing API key
            utils.get_words("test_image.jpg", words=6)

    # Define a test method for basic path sanitization
    def test_sanitize_image_path_basic(self):
        """
        Test basic path sanitization with simple content.
        """
        # Call sanitize_image_path with simple text content
        result = utils.sanitize_image_path("/photos/test.jpg", "sunset beach")
        # Assert that the result ends with the sanitized content and extension
        self.assertTrue(result.endswith("sunset-beach.jpg"))

    # Define a test method for sanitization with special characters
    def test_sanitize_image_path_with_special_chars(self):
        """
        Test that special characters are removed from content.
        """
        # Call sanitize_image_path with special characters and numbers
        result = utils.sanitize_image_path("/photos/test.jpg", "Hello, World! 123")
        # Assert that special chars and numbers are stripped out
        self.assertTrue(result.endswith("hello-world.jpg"))

    # Define a test method for extension preservation
    def test_sanitize_image_path_preserves_extension(self):
        """
        Test that the original file extension is preserved.
        """
        # Call sanitize_image_path with a PNG file
        result_png = utils.sanitize_image_path("/photos/test.png", "photo")
        # Call sanitize_image_path with a WebP file
        result_webp = utils.sanitize_image_path("/photos/test.webp", "photo")
        # Assert that the PNG extension is preserved
        self.assertTrue(result_png.endswith("photo.png"))
        # Assert that the WebP extension is preserved
        self.assertTrue(result_webp.endswith("photo.webp"))

    # Define a test method for image encoding
    def test_encode_image_returns_string(self):
        """
        Test that encode_image returns a string.
        """
        # Build the path to the test image in the assets directory
        test_image_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'test-image.jpg'
        )
        # Skip the test if the asset file does not exist
        if not os.path.exists(test_image_path):
            self.skipTest("Test image not found")
        # Call encode_image on the test image
        result = utils.encode_image(test_image_path)
        # Assert that the result is a string
        self.assertIsInstance(result, str)
        # Assert that the result is a non-empty string
        self.assertTrue(len(result) > 0)


# Check if the script is run directly
if __name__ == '__main__':
    # Run all tests in the module
    unittest.main()
