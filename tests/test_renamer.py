# -*- coding: utf-8 -*-
"""Tests for ImageRenamer rename pipeline."""

# Import standard library modules for testing
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Use try/except to handle both installed and development environments
# Attempt to import the renamer module with a fallback to the development path
try:
    # Import the renamer module from the installed package
    from ai_image_renamer import renamer
except ImportError:
    # Fallback for development/testing without installation
    # Insert the src directory at the front of the module search path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    # Import the renamer module from the development path
    from ai_image_renamer import renamer


# Define the test class for the ImageRenamer rename pipeline
class TestRenamer(unittest.TestCase):
    """Unit tests for the ImageRenamer class.

    These tests verify the renaming pipeline:
    - Validation of image files
    - AI content retrieval
    - Path sanitization
    - File rename operations

    All filesystem and API operations are mocked to ensure tests are
    fast, deterministic, and don't modify real files.
    """

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for a successful single-image rename
    def test_rename_success(self, mock_os_rename, mock_utils):
        """Test the rename function with a successful rename operation.

        This test verifies that:
        1. The image file is validated
        2. AI content is retrieved
        3. The path is sanitized
        4. os.rename is called with correct arguments
        """
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to a single test file
        args.image_paths = ["test_image.jpg"]
        # Set the desired AI description word count
        args.words = 8

        # Configure the mock to report the image as valid
        mock_utils.verify_image_file.return_value = True
        # Configure the mock to return a descriptive AI string
        mock_utils.get_words.return_value = "A test description"
        # Configure the mock to return a sanitized destination path
        mock_utils.sanitize_image_path.return_value = "a-test-description.jpg"

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify os.rename was called once with the correct source and target
        mock_os_rename.assert_called_once_with(
            "test_image.jpg",
            "a-test-description.jpg"
        )

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for renaming multiple images in a batch
    def test_rename_multiple_images(self, mock_os_rename, mock_utils):
        """Test renaming multiple images in a single batch.

        Verifies that all images in the list are processed.
        """
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to three different file types
        args.image_paths = ["image1.jpg", "image2.png", "image3.webp"]
        # Set the desired AI description word count
        args.words = 6

        # Configure the mock to report all images as valid
        mock_utils.verify_image_file.return_value = True
        # Configure get_words to yield a different description per image
        mock_utils.get_words.side_effect = ["description one", "description two", "description three"]
        # Configure sanitize_image_path to yield a different path per image
        mock_utils.sanitize_image_path.side_effect = [
            "description-one.jpg",
            "description-two.png",
            "description-three.webp"
        ]

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Assert that os.rename was called exactly three times
        self.assertEqual(mock_os_rename.call_count, 3)

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for skipping an invalid image file
    def test_rename_invalid_image(self, mock_os_rename, mock_utils):
        """Test that invalid images are skipped without renaming.

        Verifies that verify_image_file is called and invalid files
        do not trigger os.rename.
        """
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to a single test file
        args.image_paths = ["test_image.jpg"]
        # Set the desired AI description word count
        args.words = 8

        # Configure the mock to report the image as invalid
        mock_utils.verify_image_file.return_value = False

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify os.rename was never called for the invalid image
        mock_os_rename.assert_not_called()

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for handling empty AI content gracefully
    def test_rename_empty_content(self, mock_os_rename, mock_utils):
        """Test that files are skipped when AI returns empty content.

        Verifies the graceful handling of failed API responses.
        """
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to a single test file
        args.image_paths = ["test_image.jpg"]
        # Set the desired AI description word count
        args.words = 8

        # Configure the mock to report the image as valid
        mock_utils.verify_image_file.return_value = True
        # Configure get_words to return an empty string  # Empty content
        mock_utils.get_words.return_value = ""

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify os.rename was never called for empty content
        mock_os_rename.assert_not_called()

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for skipping very short target filenames
    def test_rename_short_filename(self, mock_os_rename, mock_utils):
        """Test that very short filenames are skipped.

        Filenames with length <= 3 characters are considered unusable.
        """
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to a single test file
        args.image_paths = ["test_image.jpg"]
        # Set the desired AI description word count
        args.words = 8

        # Configure the mock to report the image as valid
        mock_utils.verify_image_file.return_value = True
        # Configure get_words to return a very short string  # Very short content
        mock_utils.get_words.return_value = "ab"
        # Configure the mock to return a path with a stem of only 2 characters
        mock_utils.sanitize_image_path.return_value = "ab.jpg"

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify os.rename was never called for the short stem
        mock_os_rename.assert_not_called()

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for skipping when source equals sanitized target
    def test_rename_skips_when_target_matches_source(self, mock_os_rename, mock_utils):
        """Test that the renamer skips a file when the sanitized path matches the source."""
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image path to one where source and target will be identical
        args.image_paths = ["/tmp/same-name.jpg"]
        # Set the desired AI description word count
        args.words = 8

        # Configure the mock to report the image as valid
        mock_utils.verify_image_file.return_value = True
        # Configure get_words to return a name matching the original stem
        mock_utils.get_words.return_value = "same name"
        # Configure the mock to return the exact same path as the source
        mock_utils.sanitize_image_path.return_value = "/tmp/same-name.jpg"

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify os.rename was never called because source equals target
        mock_os_rename.assert_not_called()

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.path.exists to control target path existence checks
    @patch('ai_image_renamer.renamer.os.path.exists')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for adding a numeric suffix on name collision
    def test_rename_adds_suffix_when_target_exists(self, mock_os_rename, mock_exists, mock_utils):
        """Test that an existing destination gets a numeric suffix instead of being overwritten."""
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to a single source file
        args.image_paths = ["/tmp/source.jpg"]
        # Set the desired AI description word count
        args.words = 8

        # Configure the mock to report the image as valid
        mock_utils.verify_image_file.return_value = True
        # Configure get_words to return the target name
        mock_utils.get_words.return_value = "target name"
        # Configure the mock to return the target destination path
        mock_utils.sanitize_image_path.return_value = "/tmp/target-name.jpg"
        # Configure exists to return True for target, then False for suffixed version
        mock_exists.side_effect = [True, False]

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify os.rename was called with a suffixed destination path
        mock_os_rename.assert_called_once_with("/tmp/source.jpg", "/tmp/target-name-1.jpg")

    # Mock the utils module used by the renamer
    @patch('ai_image_renamer.renamer.utils')
    # Mock os.rename to prevent actual filesystem changes
    @patch('os.rename')
    # Define a test method for verifying the words parameter is forwarded
    def test_words_parameter_passed_to_get_words(self, mock_os_rename, mock_utils):
        """Test that the words parameter is correctly passed to get_words."""
        # Create a mock object to simulate the CLI argument namespace
        args = MagicMock()
        # Set the image paths list to a single test file
        args.image_paths = ["test_image.jpg"]
        # Set a custom word count on the mock argument namespace  # Custom word count
        args.words = 3

        # Configure the mock to report the image as valid
        mock_utils.verify_image_file.return_value = True
        # Configure get_words to return a short description
        mock_utils.get_words.return_value = "short desc"
        # Configure the mock to return a sanitized destination path
        mock_utils.sanitize_image_path.return_value = "short-desc.jpg"

        # Instantiate ImageRenamer, which triggers the rename pipeline
        renamer.ImageRenamer(args)

        # Verify get_words received the correct image path and word count
        mock_utils.get_words.assert_called_once_with("test_image.jpg", 3)


# Check if this script is being executed directly
if __name__ == '__main__':
    # Run the test suite
    unittest.main()
