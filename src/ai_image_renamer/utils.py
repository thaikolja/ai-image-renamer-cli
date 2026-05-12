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
Utility module for AI Image Renamer.

This module provides core utility functions for:
- Image file validation based on magic bytes (not file extensions)
- Base64 encoding of image files for API transmission
- Path sanitization to create SEO-friendly filenames
- AI-powered image content description via Groq API

The functions in this module are designed to work together as a pipeline:
1. verify_image_file() - Validate that a file is a supported image
2. encode_image() - Convert image to base64 for API upload
3. get_words() - Send to Groq API and receive description
4. sanitize_image_path() - Generate a clean, SEO-friendly filename
"""

# ==============================================================================
# Standard Library Imports
# ==============================================================================

# os: Provides filesystem path and file operations
# Used for: path manipulation, file existence checks, environment variables
# base64: Encoding binary data as ASCII strings
# Used for: converting image bytes to base64 for API transmission
import base64

import os

# re: Regular expression operations for text processing
# Used for: sanitizing filenames, removing non-alphabetic characters
import re

# time: Provides sleep for retry backoffs
import time

# ==============================================================================
# Third-Party Library Imports
# ==============================================================================
# filetype: Infers file type from magic bytes (file header)
# More reliable than file extensions for security and accuracy
# Supports: JPEG, PNG, GIF, WebP, and many other formats
import filetype

# Groq: Official Python client for Groq's LLM API
# Provides fast inference for multimodal models (text + images)
from groq import Groq


# ==============================================================================
# Image Validation Functions
# ==============================================================================


def verify_image_file(image_path: str) -> bool:
    """
    Determine whether the given filesystem path points to a valid image file.

    This function performs two critical validations:
    1. Verifies the path exists and points to a regular file (not directory/symlink)
    2. Infers the MIME type from magic bytes (file header), not extension

    Using magic bytes instead of file extensions provides security benefits:
    - Prevents spoofing (e.g., malicious.exe renamed to image.jpg)
    - Works correctly even if file has wrong or missing extension
    - Only reads the first few bytes, keeping the check efficient

    Args:
        image_path (str): Absolute or relative path to the candidate file.
                         Can be any string; function will handle invalid paths gracefully.

    Returns:
        bool: True if the file exists and its inferred MIME type starts with 'image/'.
              False for any of the following conditions:
              - Path does not exist
              - Path points to a directory
              - File type cannot be determined
              - File is not an image (e.g., PDF, video, executable)

    Examples:
        >>> verify_image_file("photo.jpg")
        True
        >>> verify_image_file("document.pdf")
        False
        >>> verify_image_file("/nonexistent/path.png")
        False
        >>> verify_image_file("malware.exe.jpg")  # Spoofed extension
        False

    Note:
        This function never raises exceptions for invalid inputs.
        It returns False instead, making it safe for bulk filtering workflows.
    """
    # Step 1: Check if path exists and is a regular file
    # os.path.isfile() returns False for directories, symlinks, and non-existent paths
    if not os.path.isfile(image_path):
        return False

    # Step 2: Infer MIME type from file's magic bytes (header)
    # filetype.guess() reads only the first ~262 bytes, keeping this fast
    # Returns None if file type cannot be determined
    mime_type = filetype.guess(image_path)

    # Step 3: Validate that we got a result and it's an image type
    # mime_type.mime format: "image/jpeg", "image/png", "video/mp4", etc.
    if not mime_type or not mime_type.mime.startswith("image/"):
        return False

    # All validation checks passed - this is a valid image file
    return True


# ==============================================================================
# Image Encoding Functions
# ==============================================================================


def encode_image(image_path: str) -> str:
    """
    Read the binary contents of an image file and return a base64-encoded string.

    Base64 encoding converts binary data into ASCII characters, which is required
    for embedding images in JSON payloads sent to the Groq API. The resulting
    string can be used in a data URL format: data:image/jpeg;base64,<encoded_data>

    Args:
        image_path (str): Filesystem path to the image file to encode.
                         Should be a valid path to an existing image file.

    Returns:
        str: Base64 encoded representation of the image file contents.
             This is a UTF-8 string containing only ASCII-safe characters
             (A-Z, a-z, 0-9, +, /, =).

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
        PermissionError: If the process lacks read permissions for the file.
        OSError: If the file cannot be opened or read (disk error, etc.).

    Example:
        >>> encoded = encode_image("photo.jpg")
        >>> encoded[:50]  # First 50 chars of base64 string
        '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBw'
        >>> len(encoded)  # Length depends on file size
        123456

    Note:
        The returned string does NOT include the data URL prefix.
        Callers must prepend "data:image/jpeg;base64," when constructing URLs.
    """
    # Open file in binary read mode ('rb')
    # Binary mode is essential - text mode would corrupt image data
    with open(image_path, "rb") as image_file:
        # Read entire file contents into memory
        # For large files, consider chunked reading in production
        binary_data = image_file.read()

        # Encode binary data to base64 bytes, then decode to UTF-8 string
        # b64encode returns bytes; decode() converts to str for JSON compatibility
        return base64.b64encode(binary_data).decode("utf-8")


# ==============================================================================
# Path Sanitization Functions
# ==============================================================================


def sanitize_image_path(image_path: str, image_content: str) -> str:
    """
    Generate a sanitized, SEO-friendly file path from image description.

    This function transforms a descriptive text string into a clean filename:
    1. Converts to lowercase for consistency
    2. Removes all non-alphabetic characters (keeps only a-z and spaces)
    3. Replaces whitespace sequences with single hyphens
    4. Preserves the original file extension

    The resulting filename is:
    - URL-safe (no special characters)
    - SEO-friendly (hyphen-separated keywords)
    - Cross-platform compatible (no reserved characters)

    Args:
        image_path (str): Original file path. Used to extract:
                         - Directory path (preserved in output)
                         - File extension (preserved in output)
        image_content (str): Descriptive text to convert into filename.
                            Typically AI-generated description of the image.
                            Example: "A beautiful sunset over the ocean"

    Returns:
        str: Sanitized absolute path with the new filename.
             Format: /original/directory/beautiful-sunset-over-ocean.jpg
             Returns very short paths (<4 chars) if content is mostly non-alphabetic.

    Examples:
        >>> sanitize_image_path("/photos/IMG_001.jpg", "sunset beach")
        '/photos/sunset-beach.jpg'

        >>> sanitize_image_path("pic.PNG", "Dog Running in Park!")
        '/absolute/path/to/dog-running-in-park.png'

        >>> sanitize_image_path("test.jpg", "123!!!")  # No alphabetic content
        '/absolute/path/to/.jpg'  # Empty slug

    Note:
        The function always returns an absolute path, even for relative inputs.
        If the sanitized name is empty or very short, the result may be unusable.
        Callers should check the returned path length before using it.
    """
    # Step 1: Extract the absolute directory path
    # os.path.abspath() resolves relative paths and symlinks
    # os.path.dirname() returns everything before the final slash
    dir_path = os.path.abspath(os.path.dirname(image_path))

    # Step 2: Preserve the original file extension (case-normalized)
    # os.path.splitext() returns (basename_without_ext, extension)
    # Lowercase ensures consistency across operating systems
    extension = os.path.splitext(image_path)[1].lower()

    # Step 3: Lowercase the AI-generated description for consistency
    # This ensures "Sunset Beach" and "sunset beach" produce same result
    lower_content = image_content.lower()

    # Step 4: Remove all non-alphabetic characters (except spaces)
    # Regex [^a-z\s] matches anything NOT a-z or whitespace
    # Replace matched characters with a space to maintain word boundaries
    clean_content = re.sub(r"[^a-z\s]+", " ", lower_content)

    # Step 5: Collapse whitespace sequences into single hyphens
    # \s+ matches one or more whitespace characters (space, tab, newline)
    # strip('-') removes leading/trailing hyphens from the result
    slug = re.sub(r"\s+", "-", clean_content).strip("-")

    # Step 6: Construct the final path
    # os.path.join() handles path separator correctly across platforms
    return os.path.join(dir_path, f"{slug}{extension}")


def _guess_image_mime_type(image_path: str) -> str:
    """Return the detected image MIME type, falling back to JPEG."""

    kind = filetype.guess(image_path)
    if kind and kind.mime.startswith("image/"):
        return kind.mime

    return "image/jpeg"


# ==============================================================================
# AI Content Generation Functions
# ==============================================================================


_RETRY_MAX = 3
_RETRY_BACKOFF_BASE = 2.0
_REQUEST_TIMEOUT = 30.0

_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"


def get_words(image_path: str, words: int = 6) -> str:
    """
    Generate a concise, SEO-friendly description for an image using AI.

    Sends an image to the Groq multimodal API (Llama 4 Scout) and receives
    a short text description suitable for use as a filename.

    Includes automatic retry with exponential backoff for transient failures.

    Args:
        image_path: Filesystem path to the image to analyze.
        words: Maximum number of words requested in the description (1-50).

    Returns:
        AI-generated description, or empty string on failure after retries.

    Raises:
        RuntimeError: If GROQ_API_KEY environment variable is not set.
        FileNotFoundError: If image_path does not exist.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it using: export GROQ_API_KEY='your-key-here' "
            "Get a free key at: https://console.groq.com/keys"
        )

    encoded_image = encode_image(image_path)
    image_mime_type = _guess_image_mime_type(image_path)

    word_label = "word" if words == 1 else "words"

    request_messages = [
        {
            "role":    "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "What's in this image? Describe the content of this image "
                        f"with no more than {words} {word_label} in an SEO-friendly way"
                    ),
                },
                {
                    "type":      "image_url",
                    "image_url": {
                        "url": f"data:{image_mime_type};base64,{encoded_image}"
                    },
                },
            ],
        }
    ]

    request_payload = {
        "model":       _MODEL_ID,
        "temperature": 2.0,
        "stream":      False,
        "stop":        None,
        "messages":    request_messages,
    }

    client = Groq(api_key=groq_api_key, timeout=_REQUEST_TIMEOUT)
    last_exception = None

    for attempt in range(1, _RETRY_MAX + 1):
        try:
            completion = client.chat.completions.create(**request_payload)

            if not completion or not completion.choices:
                return ""
            if not completion.choices[0].message:
                return ""
            if not completion.choices[0].message.content:
                return ""

            return completion.choices[0].message.content

        except Exception as exc:
            last_exception = exc
            if attempt < _RETRY_MAX:
                delay = _RETRY_BACKOFF_BASE ** attempt
                print(
                    f"API call failed (attempt {attempt}/{_RETRY_MAX}), "
                    f"retrying in {delay:.1f}s: {exc}",
                    file=__import__("sys").stderr,
                )
                time.sleep(delay)
            else:
                print(
                    f"API call failed after {_RETRY_MAX} attempts: {exc}",
                    file=__import__("sys").stderr,
                )

    return ""
