#  -*- coding: utf-8 -*-
#
#  AI Image Renamer
#
#  Copyright (C) 2025 Kolja Nolte
#  https://www.kolja-nolte.com
#  kolja.nolte@gmail.com
#
#  This work is licensed under the MIT License. You are free to use, modify, and distribute this work, provided that you include the copyright notice and this permission notice in all copies or substantial portions of the work. For more information, visit: https://opensource.org/licenses/MIT
#
#  @author      Kolja Nolte
#  @email       kolja.nolte@gmail.com
#  @license     MIT
#  @date        2025
#  @website     https://docs.kolja-nolte.com/ai-image-renamer-cli
#  @repository  https://gitlab.com/thaikolja/ai-image-renamer

"""
Image Renamer module - Core orchestration for AI-powered image renaming.

This module provides the ImageRenamer class which orchestrates the complete
image renaming pipeline:

    Input Image → Validation → AI Analysis → Filename Generation → File Rename

The module is designed to be used as the main processing engine, receiving
parsed CLI arguments and handling the batch processing of multiple images.

Usage:
    The ImageRenamer class is typically instantiated with parsed argparse
    arguments from the CLI module:

    >>> import argparse
    >>> args = argparse.Namespace(image_paths=['photo.jpg'], words=6)
    >>> renamer = ImageRenamer(args)
    # Images are renamed automatically during initialization

Dependencies:
    - utils module: Provides validation, AI calls, and path sanitization
    - os module: Filesystem operations for renaming files
"""

# ==============================================================================
# Standard Library Imports
# ==============================================================================

# os: Operating system interface for file and directory operations
# Used for: os.rename() to rename files, os.path for path manipulation
import os

# sys: System-specific parameters for stderr output
import sys

# ==============================================================================
# Package Imports
# ==============================================================================

# Import utilities from the same package using relative import
# This provides:
# - verify_image_file(): Validate image files by magic bytes
# - get_words(): Get AI-generated description from Groq API
# - sanitize_image_path(): Generate clean, SEO-friendly filenames
from . import utils


# ==============================================================================
# Main Image Renamer Class
# ==============================================================================

class ImageRenamer:
    """
    Orchestrates the AI-powered image renaming process.

    This class is the main processing engine for the application. It receives
    a list of image paths and processes each one through a pipeline:

    1. **Validation**: Check if the file is a valid, supported image
    2. **AI Analysis**: Send image to Groq API for content description
    3. **Sanitization**: Generate a clean, SEO-friendly filename
    4. **Rename**: Perform the actual file system rename operation

    The class is designed for batch processing and handles errors gracefully:
    - Invalid files are skipped with a warning message
    - Failed API calls skip the file without crashing
    - Progress messages inform the user of each step

    Attributes:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - image_paths (list): List of file paths to process
            - words (int): Maximum words in generated filename
        image_paths (list): Convenience reference to args.image_paths

    Example:
        >>> import argparse
        >>> args = argparse.Namespace(
        ...     image_paths=['vacation.jpg', 'family.png'],
        ...     words=5
        ... )
        >>> renamer = ImageRenamer(args)
        Processing vacation.jpg...
        Renamed vacation.jpg to /photos/sunny-beach-sunset.jpg
        Processing family.png...
        Renamed family.png to /photos/family-portrait-smile.png

    Note:
        The rename operation happens automatically in __init__.
        There is no need to call rename() manually unless processing
        images incrementally after initialization.
    """

    def __init__(self, args):
        """
        Initialize the ImageRenamer and process all specified images.

        This constructor stores the arguments and immediately begins processing
        all image paths through the rename pipeline. Each image is processed
        independently, so failures don't affect other files.

        Args:
            args (argparse.Namespace): Parsed CLI arguments containing:
                - image_paths (list[str]): One or more paths to image files
                - words (int): Maximum number of words for the new filename
                              (passed to AI prompt, actual count may vary)

        Returns:
            None: The constructor performs side effects (file renames) but
                  returns nothing.

        Side Effects:
            - Renames files on the filesystem
            - Prints progress messages to stdout
            - May raise exceptions from underlying operations

        Example:
            >>> args = argparse.Namespace(image_paths=['test.jpg'], words=6)
            >>> renamer = ImageRenamer(args)
            Processing test.jpg...
            Renamed test.jpg to /path/to/descriptive-name.jpg
        """
        # Store the complete arguments object for access to all CLI options
        self.args = args

        # Convenience reference to the image paths list
        # This is the primary data we iterate over in rename()
        self.image_paths = args.image_paths

        # Begin processing immediately
        # This design allows simple instantiation: ImageRenamer(args)
        self.rename()

    def rename(self):
        """
        Process and rename all images in the image_paths list.

        Each image is analyzed via the Groq API (fresh call per image),
        validated, and renamed to an SEO-friendly filename based on its content.
        Progress goes to stderr; final summary goes to stdout.

        Returns:
            None: Performs side effects only (file renames, output).
        """
        succeeded = 0
        skipped = 0
        failed = 0

        for path in self.image_paths:

            if not utils.verify_image_file(path):
                print(f"Skipping invalid image file: {path}", file=sys.stderr)
                skipped += 1
                continue

            print(f"Processing {path}...", file=sys.stderr)

            content = utils.get_words(path, self.args.words)

            if not content:
                print(f"Failed to retrieve content from image: {path}", file=sys.stderr)
                failed += 1
                continue

            new_path = utils.sanitize_image_path(path, content)

            if os.path.abspath(path) == os.path.abspath(new_path):
                print(f"File already has target name, skipping: {path}", file=sys.stderr)
                skipped += 1
                continue

            base_path, extension = os.path.splitext(new_path)
            candidate_path = new_path
            suffix = 1
            while os.path.exists(candidate_path):
                candidate_path = f"{base_path}-{suffix}{extension}"
                suffix += 1

            stem = os.path.splitext(os.path.basename(candidate_path))[0]
            if len(stem) <= 3:
                print(f"Generated filename too short, skipping: {path}", file=sys.stderr)
                skipped += 1
                continue

            os.rename(path, candidate_path)
            succeeded += 1

            print(f"Renamed {path} to {candidate_path}", file=sys.stderr)

        summary = (
            f"Done: {succeeded} renamed, {skipped} skipped, {failed} failed "
            f"(out of {len(self.image_paths)})"
        )
        print(summary)
