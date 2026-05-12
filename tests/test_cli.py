# -*- coding: utf-8 -*-
"""Tests for CLI argument parsing and env loading."""

# Import standard library modules
import io
import unittest
from unittest.mock import patch
import os
import sys

# Attempt to import the CLI module, falling back to development path
try:
    # Import CLI from installed package
    from ai_image_renamer import cli
except ImportError:
    # Add src directory to the module search path for dev environments
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    # Import CLI after adjusting the Python path
    from ai_image_renamer import cli


# Define the test case class for CLI tests
class TestCLI(unittest.TestCase):
    """
    Unit tests for the command-line interface functions.

    These tests verify:
    - Correct argument parsing for various inputs
    - Default values for optional arguments
    - Error handling for invalid arguments
    - Integration with the ImageRenamer class
    """

    # Mock the ImageRenamer class to prevent real instantiation
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function to prevent .env file loading
    @patch('dotenv.load_dotenv')
    # Define test for main() with a single image path
    def test_main_with_single_image(self, mock_load_dotenv, mock_renamer):
        """
        Test main() with a single image path.

        Verifies that:
        - load_dotenv is called
        - ImageRenamer is instantiated with correct arguments
        """
        # Arrange: Set up command line arguments
        with patch('sys.argv', ['rename-images', 'image.jpg']):
            # Act: Call main
            cli.main()

            # Assert: ImageRenamer should be called
            self.assertTrue(mock_renamer.called)

            # Assert: Check the arguments passed to ImageRenamer
            call_args = mock_renamer.call_args[0][0]
            # Verify the image paths match the provided argument
            self.assertEqual(call_args.image_paths, ['image.jpg'])

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for main() with multiple image paths
    def test_main_with_multiple_images(self, mock_load_dotenv, mock_renamer):
        """
        Test main() with multiple image paths.
        """
        # Arrange: Set up command line arguments with multiple images
        with patch('sys.argv', ['rename-images', 'img1.jpg', 'img2.png', 'img3.webp']):
            # Act: Call main
            cli.main()

            # Assert: Check all images are in the arguments
            call_args = mock_renamer.call_args[0][0]
            # Verify all three image paths were captured
            self.assertEqual(call_args.image_paths, ['img1.jpg', 'img2.png', 'img3.webp'])

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for main() with custom word count
    def test_main_with_words_option(self, mock_load_dotenv, mock_renamer):
        """
        Test main() with custom word count option.
        """
        # Arrange: Set up command line with --words option
        with patch('sys.argv', ['rename-images', '-w', '5', 'image.jpg']):
            # Act: Call main
            cli.main()

            # Assert: Check words parameter
            call_args = mock_renamer.call_args[0][0]
            # Verify the word count was parsed correctly
            self.assertEqual(call_args.words, 5)

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for default word count
    def test_main_default_words(self, mock_load_dotenv, mock_renamer):
        """
        Test that default word count is 6.
        """
        # Arrange: Set up command line without --words option
        with patch('sys.argv', ['rename-images', 'image.jpg']):
            # Act: Call main
            cli.main()

            # Assert: Default words should be 6
            call_args = mock_renamer.call_args[0][0]
            # Verify the default word count value
            self.assertEqual(call_args.words, 6)

    # Define test for missing image paths
    def test_main_no_images_raises_error(self):
        """
        Test that missing image paths raises SystemExit.

        argparse exits with error when required positional args are missing.
        """
        # Arrange: Set up command line without image paths
        with patch('sys.argv', ['rename-images']):
            # Act & Assert: Should raise SystemExit
            with self.assertRaises(SystemExit):
                cli.main()

    # Define test for invalid word count value
    def test_main_invalid_words_value(self):
        """
        Test that invalid word count raises SystemExit.

        Words must be in range 1-50.
        """
        # Arrange: Set up command line with invalid word count
        with patch('sys.argv', ['rename-images', '-w', '51', 'image.jpg']):
            # Act & Assert: Should raise SystemExit due to choices validation
            with self.assertRaises(SystemExit):
                cli.main()

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for maximum word count boundary
    def test_main_allows_max_words_value(self, mock_load_dotenv, mock_renamer):
        """
        Test that the maximum supported word count of 50 is accepted.
        """
        with patch('sys.argv', ['rename-images', '-w', '50', 'image.jpg']):
            cli.main()

        call_args = mock_renamer.call_args[0][0]
        # Verify the maximum word count of 50 is accepted
        self.assertEqual(call_args.words, 50)

    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for version display fallback
    def test_version_uses_source_fallback(self, mock_load_dotenv):
        """
        Test that --version works even when package metadata is unavailable.
        """
        # Create a string buffer to capture stdout output
        stdout = io.StringIO()

        # Redirect stdout to the buffer for inspection
        with patch('sys.stdout', stdout):
            # Patch sys.argv with the --version flag
            with patch('sys.argv', ['rename-images', '--version']):
                # Mock _get_version to return a fixed version string
                with patch('ai_image_renamer.cli._get_version', return_value='1.1.0'):
                    # Expect SystemExit when version is displayed
                    with self.assertRaises(SystemExit) as exc:
                        # Invoke the CLI main function
                        cli.main()

        # Verify the exit code is 0 (success)
        self.assertEqual(exc.exception.code, 0)
        # Verify the printed version string matches expected format
        self.assertEqual(stdout.getvalue().strip(), 'rename-images 1.1.0')

    # Define test for zero word count
    def test_main_zero_words_raises_error(self):
        """
        Test that zero words raises SystemExit.

        Words must be at least 1.
        """
        # Arrange: Set up command line with zero words
        with patch('sys.argv', ['rename-images', '-w', '0', 'image.jpg']):
            # Act & Assert: Should raise SystemExit
            with self.assertRaises(SystemExit):
                cli.main()

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for truncation beyond max images
    def test_main_truncates_to_max_images(self, mock_load_dotenv, mock_renamer):
        """
        Test that more than 3 images are truncated to 3 with a warning.
        """
        with patch('sys.argv', ['rename-images', 'img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg']):
            cli.main()

        call_args = mock_renamer.call_args[0][0]
        # Verify the list was truncated to exactly 3 images
        self.assertEqual(len(call_args.image_paths), 3)
        # Verify only the first three images are kept
        self.assertEqual(call_args.image_paths, ['img1.jpg', 'img2.jpg', 'img3.jpg'])

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for exactly three images (no truncation)
    def test_main_exactly_three_images_not_truncated(self, mock_load_dotenv, mock_renamer):
        """
        Test that exactly 3 images are not truncated.
        """
        with patch('sys.argv', ['rename-images', 'a.jpg', 'b.jpg', 'c.jpg']):
            cli.main()

        call_args = mock_renamer.call_args[0][0]
        # Verify all three images are preserved
        self.assertEqual(len(call_args.image_paths), 3)

    # Mock the ImageRenamer class
    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    # Mock the load_dotenv function
    @patch('dotenv.load_dotenv')
    # Define test for load_dotenv invocation
    def test_load_dotenv_called(self, mock_load_dotenv, mock_renamer):
        """
        Test that load_dotenv is called at startup.

        This ensures environment variables from .env files are loaded.
        """
        # Arrange: Set up command line arguments
        with patch('sys.argv', ['rename-images', 'image.jpg']):
            # Act: Call main
            cli.main()

            # Assert: load_dotenv should be called once
            mock_load_dotenv.assert_called_once()


# Check if this script is executed directly
if __name__ == '__main__':
    # Run all tests in this module
    unittest.main()
