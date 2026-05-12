#  AI Image Renamer
#
#  Copyright (C) 2026 Kolja Nolte
#  https://www.kolja-nolte.com
#  kolja.nolte@gmail.com
#
#  This work is licensed under the MIT License. You are free to use, modify, and distribute this work, provided that you include the copyright notice and this permission notice in all copies or substantial portions of the work. For more information, visit: https://opensource.org/licenses/MIT
#
#  @author      Kolja Nolte
#  @email       kolja.nolte@gmail.com
#  @license     MIT
#  @date        2026
#  @website     https://docs.kolja-nolte.com/ai-image-renamer
#  @repository  https://gitlab.com/thaikolja/ai-image-renamer

"""Core rename pipeline orchestrator."""

# Import operating system and system-specific interfaces
import os
import sys

# Import utility functions for image validation, AI analysis, and path sanitization
from . import utils


# Define the main renamer class that orchestrates AI-powered image renaming
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

    # Initialize the renamer instance with parsed CLI arguments
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
            >>> arguments = argparse.Namespace(image_paths=['test.jpg'], words=6)
            >>> renamer = ImageRenamer(arguments)
            Processing test.jpg...
            Renamed test.jpg to /path/to/descriptive-name.jpg
        """
        # Store the parsed CLI arguments for later access
        self.args = args

        # Extract image paths from arguments for iteration
        self.image_paths = args.image_paths

        # Start the rename pipeline immediately upon construction
        self.rename()

    # Process and rename all images in the paths list
    def rename(self):
        """
        Process and rename all images in the image_paths list.

        Each image is analyzed via the Groq API (fresh call per image),
        validated, and renamed to an SEO-friendly filename based on its content.
        Progress goes to stderr; final summary goes to stdout.

        Returns:
            None: Performs side effects only (file renames, output).
        """
        # Initialize counter for successfully renamed files
        succeeded = 0
        # Initialize counter for skipped files
        skipped = 0
        # Initialize counter for failed files
        failed = 0

        # Iterate over each image path provided by the user
        for path in self.image_paths:

            # Check if the file is a valid image via magic byte detection
            if not utils.verify_image_file(path):
                # Print a warning about the invalid file to stderr
                print(f"Skipping invalid image file: {path}", file=sys.stderr)
                # Increment the skipped counter
                skipped += 1
                # Move to the next image path
                continue

            # Inform the user that processing has started for this image
            print(f"Processing {path}...", file=sys.stderr)

            # Fetch AI-generated content description from the Groq API
            content = utils.get_words(path, self.args.words)

            # Check if the API returned meaningful content
            if not content:
                # Print an error message about the failed content retrieval
                print(f"Failed to retrieve content from image: {path}", file=sys.stderr)
                # Increment the failed counter
                failed += 1
                # Skip to the next image without renaming
                continue

            # Generate a sanitized, SEO-friendly filename from the AI description
            new_path = utils.sanitize_image_path(path, content)

            # Check if the sanitized path is identical to the original path
            if os.path.abspath(path) == os.path.abspath(new_path):
                # Notify the user that the file already has the target name
                print(f"File already has target name, skipping: {path}", file=sys.stderr)
                # Increment the skipped counter
                skipped += 1
                # Move to the next image since no rename is needed
                continue

            # Split the new path into base and extension components
            base_path, extension = os.path.splitext(new_path)
            # Set the initial candidate path to the sanitized path
            candidate_path = new_path
            # Initialize the numeric suffix counter for deduplication
            suffix = 1
            # Keep incrementing the suffix until a non-existent path is found
            while os.path.exists(candidate_path):
                # Generate a new candidate path with an incremented numeric suffix
                candidate_path = f"{base_path}-{suffix}{extension}"
                # Increment the suffix counter for the next attempt
                suffix += 1

            # Extract the filename stem (without extension) for length validation
            stem = os.path.splitext(os.path.basename(candidate_path))[0]
            # Check if the generated stem is too short to be meaningful
            if len(stem) <= 3:
                # Print a warning about the too-short filename
                print(f"Generated filename too short, skipping: {path}", file=sys.stderr)
                # Increment the skipped counter
                skipped += 1
                # Skip to the next image without renaming
                continue

            # Perform the actual file system rename operation
            os.rename(path, candidate_path)
            # Increment the succeeded counter
            succeeded += 1

            # Notify the user that the file was successfully renamed
            print(f"Renamed {path} to {candidate_path}", file=sys.stderr)

        # Build a summary string with counts of renamed, skipped, and failed files
        summary = (
            f"Done: {succeeded} renamed, {skipped} skipped, {failed} failed "
            f"(out of {len(self.image_paths)})"
        )
        # Print the final summary to stdout
        print(summary)
