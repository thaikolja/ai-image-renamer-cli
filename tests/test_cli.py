# -*- coding: utf-8 -*-
"""
Test suite for the AI Image Renamer command-line interface.

This module contains unit tests for the CLI module in ai_image_renamer.cli,
including argument parsing, validation, and integration with the renamer.

Tests cover:
- Argument parsing and validation
- Version display
- Help text generation
- Integration with ImageRenamer
"""

# ==============================================================================
# Standard Library Imports
# ==============================================================================
import io
import unittest
from unittest.mock import patch
import os
import sys

# ==============================================================================
# Package Imports
# ==============================================================================
# Use try/except to handle both installed and development environments
try:
    from ai_image_renamer import cli
except ImportError:
    # Fallback for development/testing without installation
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from ai_image_renamer import cli


# ==============================================================================
# Test Class for CLI
# ==============================================================================

class TestCLI(unittest.TestCase):
    """
    Unit tests for the command-line interface functions.

    These tests verify:
    - Correct argument parsing for various inputs
    - Default values for optional arguments
    - Error handling for invalid arguments
    - Integration with the ImageRenamer class
    """

    # ==========================================================================
    # Tests for Argument Parsing
    # ==========================================================================

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
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
            self.assertEqual(call_args.image_paths, ['image.jpg'])

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
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
            self.assertEqual(call_args.image_paths, ['img1.jpg', 'img2.png', 'img3.webp'])

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
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
            self.assertEqual(call_args.words, 5)

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
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
            self.assertEqual(call_args.words, 6)

    # ==========================================================================
    # Tests for Error Handling
    # ==========================================================================

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

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
    def test_main_allows_max_words_value(self, mock_load_dotenv, mock_renamer):
        """
        Test that the maximum supported word count of 50 is accepted.
        """
        with patch('sys.argv', ['rename-images', '-w', '50', 'image.jpg']):
            cli.main()

        call_args = mock_renamer.call_args[0][0]
        self.assertEqual(call_args.words, 50)

    @patch('ai_image_renamer.cli.load_dotenv')
    def test_version_uses_source_fallback(self, mock_load_dotenv):
        """
        Test that --version works even when package metadata is unavailable.
        """
        stdout = io.StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', ['rename-images', '--version']):
                with patch('ai_image_renamer.cli._get_version', return_value='1.1.0'):
                    with self.assertRaises(SystemExit) as exc:
                        cli.main()

        self.assertEqual(exc.exception.code, 0)
        self.assertEqual(stdout.getvalue().strip(), 'rename-images 1.1.0')

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

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
    def test_main_truncates_to_max_images(self, mock_load_dotenv, mock_renamer):
        """
        Test that more than 3 images are truncated to 3 with a warning.
        """
        with patch('sys.argv', ['rename-images', 'img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg']):
            cli.main()

        call_args = mock_renamer.call_args[0][0]
        self.assertEqual(len(call_args.image_paths), 3)
        self.assertEqual(call_args.image_paths, ['img1.jpg', 'img2.jpg', 'img3.jpg'])

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
    def test_main_exactly_three_images_not_truncated(self, mock_load_dotenv, mock_renamer):
        """
        Test that exactly 3 images are not truncated.
        """
        with patch('sys.argv', ['rename-images', 'a.jpg', 'b.jpg', 'c.jpg']):
            cli.main()

        call_args = mock_renamer.call_args[0][0]
        self.assertEqual(len(call_args.image_paths), 3)

    # ==========================================================================
    # Tests for Environment Loading
    # ==========================================================================

    @patch('ai_image_renamer.cli.renamer.ImageRenamer')
    @patch('ai_image_renamer.cli.load_dotenv')
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


# ==============================================================================
# Test Runner Entry Point
# ==============================================================================

if __name__ == '__main__':
    unittest.main()