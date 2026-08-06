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

_MOCK_OPENAI = MagicMock()
sys.modules.setdefault('openai', _MOCK_OPENAI)

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
    # Mock config.get to provide the API key
    @patch('ai_image_renamer.utils.config.get')
    # Define a test method for a successful get_words call
    def test_get_words_success(self, mock_config_get, mock_groq, mock_guess, mock_encode_image):
        """
        Test get_words function with a successful API call.

        Verifies that the function correctly extracts content from
        the Groq API response.
        """
        # Configure the mock to return a fixed encoded string
        mock_encode_image.return_value = "encoded_image_string"
        # Configure the mock to return a PNG MIME type
        mock_guess.return_value = MagicMock(mime='image/png')
        # Provide a fake API key and model via config mock
        mock_config_get.side_effect = lambda key, default=None: {
            "GROQ_API_KEY": "test-api-key",
            "MODEL": "qwen/qwen3.6-27b",
        }.get(key, default)
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
        self.assertEqual(create_kwargs["model"], "qwen/qwen3.6-27b")
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
    # Mock config.get to provide the API key
    @patch('ai_image_renamer.utils.config.get')
    def test_get_words_truncates_hyphenated_and_whitespace_words(self, mock_config_get, mock_groq, mock_guess, mock_encode_image):
        """
        Test that get_words correctly splits and truncates both hyphenated and whitespace-separated keywords.
        """
        mock_encode_image.return_value = "encoded_image_string"
        mock_guess.return_value = MagicMock(mime='image/png')
        mock_config_get.side_effect = lambda key, default=None: {
            "GROQ_API_KEY": "test-api-key",
        }.get(key, default)
        
        # Test case 1: Hyphenated words
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "computered-mac-app-interface-screen-overlay"
        mock_groq.return_value.chat.completions.create.return_value = mock_completion
        result = utils.get_words("test_image.jpg", words=4)
        self.assertEqual(result, "computered mac app interface")

        # Test case 2: Whitespace-separated words
        mock_completion.choices[0].message.content = "computered mac app interface screen overlay"
        mock_groq.return_value.chat.completions.create.return_value = mock_completion
        result = utils.get_words("test_image.jpg", words=3)
        self.assertEqual(result, "computered mac app")

    # Mock encode_image to return a fixed encoded string
    @patch('ai_image_renamer.utils.encode_image')
    # Mock filetype.guess to control MIME type detection
    @patch('filetype.guess')
    # Mock the Groq client to avoid real API calls
    @patch('groq.Groq')
    # Mock config.get to provide the API key
    @patch('ai_image_renamer.utils.config.get')
    # Define a test method for a failed get_words call
    def test_get_words_failure(self, mock_config_get, mock_groq, mock_guess, mock_encode_image):
        """
        Test get_words function with a failed API call.

        Verifies that the function returns empty string when API fails.
        """
        # Configure the mock to return a fixed encoded string
        mock_encode_image.return_value = "encoded_image_string"
        # Configure the mock to return a JPEG MIME type
        mock_guess.return_value = MagicMock(mime='image/jpeg')
        # Provide a fake API key via config mock
        mock_config_get.side_effect = lambda key, default=None: {
            "GROQ_API_KEY": "test-api-key",
        }.get(key, default)
        # Configure Groq client mock to return a failed response (None)
        mock_groq.return_value.chat.completions.create.return_value = None
        # Call get_words with test parameters
        result = utils.get_words("test_image.jpg", words=8)
        # Assert that the result is an empty string on failure
        self.assertEqual(result, "")

    # Mock config.get to return empty API key
    @patch('ai_image_renamer.utils.config.get')
    # Mock os.getenv to simulate missing environment variable
    @patch('ai_image_renamer.utils.os.getenv')
    # Define a test method for a missing API key scenario
    def test_get_words_missing_api_key(self, mock_getenv, mock_config_get):
        """
        Test that get_words raises RuntimeError when API key is missing.
        """
        # Configure the mock to return empty GROQ_API_KEY from config
        mock_config_get.side_effect = lambda key, default=None: {
            "GROQ_API_KEY": "",
        }.get(key, default)
        # Configure the mock to return None (no API key found)
        mock_getenv.return_value = None
        # Assert that calling get_words without an API key raises RuntimeError
        with self.assertRaises(RuntimeError):
            # Call get_words which should raise due to missing API key
            utils.get_words("test_image.jpg", words=6)

    # Mock encode_image to return a fixed encoded string
    @patch('ai_image_renamer.utils.encode_image')
    # Mock filetype.guess to control MIME type detection
    @patch('filetype.guess')
    # Mock the OpenAI client to avoid real API calls
    @patch('openai.OpenAI')
    # Mock config.get to provide the provider settings
    @patch('ai_image_renamer.utils.config.get')
    def test_get_words_ollama_success(self, mock_config_get, mock_openai, mock_guess, mock_encode_image):
        """
        Test get_words with the ollama provider and a successful API call.
        """
        # Configure the mock to return a fixed encoded string
        mock_encode_image.return_value = "encoded_image_string"
        # Configure the mock to return a PNG MIME type
        mock_guess.return_value = MagicMock(mime='image/png')
        # Provide Ollama settings via config mock
        mock_config_get.side_effect = lambda key, default=None: {
            "PROVIDER": "ollama",
            "OLLAMA_HOST": "http://localhost:11434/v1",
            "OLLAMA_MODEL": "llava:latest",
        }.get(key, default)
        # Create a mock completion object
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "A test description"
        # Configure the OpenAI client mock to return the completion
        mock_openai.return_value.chat.completions.create.return_value = mock_completion
        # Call get_words with the ollama provider
        result = utils.get_words("test_image.jpg", words=8)
        # Assert that the result matches the mocked description
        self.assertEqual(result, "A test description")
        # Capture the kwargs passed to the OpenAI client constructor
        client_kwargs = mock_openai.call_args.kwargs
        # Assert that the Ollama endpoint is used
        self.assertEqual(client_kwargs["base_url"], "http://localhost:11434/v1")
        # Assert that the dummy Ollama API key is used
        self.assertEqual(client_kwargs["api_key"], "ollama")
        # Capture the kwargs passed to the API create call
        create_kwargs = mock_openai.return_value.chat.completions.create.call_args.kwargs
        # Assert that the correct model name was used
        self.assertEqual(create_kwargs["model"], "llava:latest")
        # Assert that the vision URL includes the correct MIME type and encoded image
        self.assertEqual(
            create_kwargs["messages"][0]["content"][1]["image_url"]["url"],
            "data:image/png;base64,encoded_image_string",
        )

    # Mock encode_image to return a fixed encoded string
    @patch('ai_image_renamer.utils.encode_image')
    # Mock filetype.guess to control MIME type detection
    @patch('filetype.guess')
    # Mock the OpenAI client to avoid real API calls
    @patch('openai.OpenAI')
    # Mock config.get to provide the provider settings
    @patch('ai_image_renamer.utils.config.get')
    def test_get_words_openai_success(self, mock_config_get, mock_openai, mock_guess, mock_encode_image):
        """
        Test get_words with the openai provider and a successful API call.
        """
        # Configure the mock to return a fixed encoded string
        mock_encode_image.return_value = "encoded_image_string"
        # Configure the mock to return a JPEG MIME type
        mock_guess.return_value = MagicMock(mime='image/jpeg')
        # Provide OpenAI-compatible settings via config mock
        mock_config_get.side_effect = lambda key, default=None: {
            "PROVIDER": "openai",
            "OPENAI_API_BASE": "http://localhost:1234/v1",
            "OPENAI_MODEL": "my-vision-model",
            "OPENAI_API_KEY": "local-key",
        }.get(key, default)
        # Create a mock completion object
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "A test description"
        # Configure the OpenAI client mock to return the completion
        mock_openai.return_value.chat.completions.create.return_value = mock_completion
        # Call get_words with the openai provider
        result = utils.get_words("test_image.jpg", words=8)
        # Assert that the result matches the mocked description
        self.assertEqual(result, "A test description")
        # Capture the kwargs passed to the OpenAI client constructor
        client_kwargs = mock_openai.call_args.kwargs
        # Assert that the custom endpoint is used
        self.assertEqual(client_kwargs["base_url"], "http://localhost:1234/v1")
        # Assert that the configured API key is used
        self.assertEqual(client_kwargs["api_key"], "local-key")
        # Capture the kwargs passed to the API create call
        create_kwargs = mock_openai.return_value.chat.completions.create.call_args.kwargs
        # Assert that the correct model name was used
        self.assertEqual(create_kwargs["model"], "my-vision-model")

    # Mock config.get to provide the provider settings
    @patch('ai_image_renamer.utils.config.get')
    def test_get_words_ollama_missing_openai_package(self, mock_config_get):
        """
        Test that get_words raises RuntimeError when openai is not installed.
        """
        # Provide Ollama settings via config mock
        mock_config_get.side_effect = lambda key, default=None: {
            "PROVIDER": "ollama",
            "OLLAMA_HOST": "http://localhost:11434/v1",
            "OLLAMA_MODEL": "llava:latest",
        }.get(key, default)
        # Simulate the openai package being unavailable
        with patch.dict(sys.modules, {"openai": None}):
            # Assert that calling get_words raises RuntimeError
            with self.assertRaises(RuntimeError):
                utils.get_words("test_image.jpg", words=6)

    # Mock config.get to provide the provider settings
    @patch('ai_image_renamer.utils.config.get')
    def test_get_words_openai_missing_base_url(self, mock_config_get):
        """
        Test that get_words raises RuntimeError when OPENAI_API_BASE is missing.
        """
        # Provide provider settings with no API base
        mock_config_get.side_effect = lambda key, default=None: {
            "PROVIDER": "openai",
            "OPENAI_MODEL": "my-vision-model",
        }.get(key, default)
        # Assert that calling get_words raises RuntimeError
        with self.assertRaises(RuntimeError):
            utils.get_words("test_image.jpg", words=6)

    # Define a test method for an unknown provider
    def test_get_words_unknown_provider_raises_value_error(self):
        """
        Test that get_words raises ValueError for an unknown provider.
        """
        # Assert that calling get_words with an unknown provider raises ValueError
        with self.assertRaises(ValueError):
            utils.get_words("test_image.jpg", words=6, provider="unknown")

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

    # Define a test method for long keyword truncation
    def test_sanitize_image_path_does_not_cut_keywords(self):
        """Test that truncation happens at keyword boundaries."""
        # Force a short filename cap to trigger truncation.
        with patch('ai_image_renamer.utils.config.get', return_value='25'):
            result = utils.sanitize_image_path(
                "/photos/test.jpg",
                "alpha beta gamma delta epsilon",
            )

        # Should stop before cutting the last keyword in half.
        self.assertTrue(result.endswith("alpha-beta-gamma-delta.jpg"))

    # Define a test method for one long keyword
    def test_sanitize_image_path_keeps_single_long_keyword(self):
        """Test that a single long keyword is not cut mid-word."""
        with patch('ai_image_renamer.utils.config.get', return_value='10'):
            result = utils.sanitize_image_path(
                "/photos/test.jpg",
                "supercalifragilisticexpialidocious",
            )

        self.assertTrue(result.endswith("supercalifragilisticexpialidocious.jpg"))

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
