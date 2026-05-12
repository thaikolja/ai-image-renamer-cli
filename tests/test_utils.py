# -*- coding: utf-8 -*-
"""
Test suite for the AI Image Renamer utility functions.

This module contains unit tests for the functions in ai_image_renamer.utils:
- verify_image_file: Image file validation
- encode_image: Base64 encoding
- sanitize_image_path: Filename sanitization
- get_words: AI content generation

All tests use unittest.mock to avoid actual API calls during testing.
"""

# ==============================================================================
# Standard Library Imports
# ==============================================================================
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile

# ==============================================================================
# Package Imports
# ==============================================================================
# Use try/except to handle both installed and development environments
try:
    from ai_image_renamer import utils
except ImportError:
    # Fallback for development/testing without installation
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from ai_image_renamer import utils


# ==============================================================================
# Test Class for Utility Functions
# ==============================================================================

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

    # ==========================================================================
    # Tests for verify_image_file()
    # ==========================================================================

    def test_verify_image_file_with_valid_image(self):
        """
        Test that verify_image_file returns True for a valid image file.

        Uses a test image from the assets directory.
        """
        # Arrange: Get path to test image
        test_image_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'test-image.jpg'
        )

        # Skip test if file doesn't exist (CI environment)
        if not os.path.exists(test_image_path):
            self.skipTest("Test image not found")

        # Act: Verify the image file
        result = utils.verify_image_file(test_image_path)

        # Assert: Should return True for valid image
        self.assertTrue(result)

    def test_verify_image_file_with_nonexistent_file(self):
        """
        Test that verify_image_file returns False for non-existent file.

        The function should handle missing files gracefully without raising.
        """
        # Act: Verify non-existent file
        result = utils.verify_image_file('/nonexistent/path/image.jpg')

        # Assert: Should return False, not raise exception
        self.assertFalse(result)

    def test_verify_image_file_with_non_image_file(self):
        """
        Test that verify_image_file returns False for non-image files.

        Creates a temporary text file and verifies it's rejected.
        """
        # Arrange: Create temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"This is not an image")
            temp_path = temp_file.name

        try:
            # Act: Verify the non-image file
            result = utils.verify_image_file(temp_path)

            # Assert: Should return False for non-image
            self.assertFalse(result)
        finally:
            # Cleanup: Remove temporary file
            os.unlink(temp_path)

    # ==========================================================================
    # Tests for get_words()
    # ==========================================================================

    @patch('ai_image_renamer.utils.encode_image')
    @patch('ai_image_renamer.utils.filetype.guess')
    @patch('ai_image_renamer.utils.Groq')
    def test_get_words_success(self, mock_groq, mock_guess, mock_encode_image):
        """
        Test get_words function with a successful API call.

        Verifies that the function correctly extracts content from
        the Groq API response.
        """
        # Arrange: Mock the encode_image function
        mock_encode_image.return_value = "encoded_image_string"

        # Arrange: Mock MIME detection for a PNG image
        mock_guess.return_value = MagicMock(mime='image/png')

        # Arrange: Mock the Groq client and response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "A test description"
        mock_groq.return_value.chat.completions.create.return_value = mock_completion

        # Act: Call get_words
        result = utils.get_words("test_image.jpg", words=8)

        # Assert: Should return the mocked description
        self.assertEqual(result, "A test description")

        # Assert: The vision payload should use the detected MIME type
        create_kwargs = mock_groq.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs["model"], "meta-llama/llama-4-scout-17b-16e-instruct")
        self.assertEqual(
            create_kwargs["messages"][0]["content"][1]["image_url"]["url"],
            "data:image/png;base64,encoded_image_string",
        )

    @patch('ai_image_renamer.utils.encode_image')
    @patch('ai_image_renamer.utils.filetype.guess')
    @patch('ai_image_renamer.utils.Groq')
    def test_get_words_failure(self, mock_groq, mock_guess, mock_encode_image):
        """
        Test get_words function with a failed API call.

        Verifies that the function returns empty string when API fails.
        """
        # Arrange: Mock the encode_image function
        mock_encode_image.return_value = "encoded_image_string"

        # Arrange: Mock MIME detection for the input image
        mock_guess.return_value = MagicMock(mime='image/jpeg')

        # Arrange: Mock failed API response (None)
        mock_groq.return_value.chat.completions.create.return_value = None

        # Act: Call get_words
        result = utils.get_words("test_image.jpg", words=8)

        # Assert: Should return empty string on failure
        self.assertEqual(result, "")

    @patch('ai_image_renamer.utils.os.getenv')
    def test_get_words_missing_api_key(self, mock_getenv):
        """
        Test that get_words raises RuntimeError when API key is missing.
        """
        # Arrange: Mock missing API key
        mock_getenv.return_value = None

        # Act & Assert: Should raise RuntimeError
        with self.assertRaises(RuntimeError):
            utils.get_words("test_image.jpg", words=6)

    # ==========================================================================
    # Tests for sanitize_image_path()
    # ==========================================================================

    def test_sanitize_image_path_basic(self):
        """
        Test basic path sanitization with simple content.
        """
        # Act: Sanitize path with simple content
        result = utils.sanitize_image_path("/photos/test.jpg", "sunset beach")

        # Assert: Should produce clean hyphenated filename
        self.assertTrue(result.endswith("sunset-beach.jpg"))

    def test_sanitize_image_path_with_special_chars(self):
        """
        Test that special characters are removed from content.
        """
        # Act: Sanitize path with special characters
        result = utils.sanitize_image_path("/photos/test.jpg", "Hello, World! 123")

        # Assert: Special chars and numbers should be removed
        self.assertTrue(result.endswith("hello-world.jpg"))

    def test_sanitize_image_path_preserves_extension(self):
        """
        Test that the original file extension is preserved.
        """
        # Act: Sanitize paths with different extensions
        result_png = utils.sanitize_image_path("/photos/test.png", "photo")
        result_webp = utils.sanitize_image_path("/photos/test.webp", "photo")

        # Assert: Extensions should be preserved and lowercase
        self.assertTrue(result_png.endswith("photo.png"))
        self.assertTrue(result_webp.endswith("photo.webp"))

    # ==========================================================================
    # Tests for encode_image()
    # ==========================================================================

    def test_encode_image_returns_string(self):
        """
        Test that encode_image returns a string.
        """
        # Arrange: Get path to test image
        test_image_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'test-image.jpg'
        )

        # Skip test if file doesn't exist
        if not os.path.exists(test_image_path):
            self.skipTest("Test image not found")

        # Act: Encode the image
        result = utils.encode_image(test_image_path)

        # Assert: Should return a non-empty string
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


# ==============================================================================
# Test Runner Entry Point
# ==============================================================================

if __name__ == '__main__':
    unittest.main()