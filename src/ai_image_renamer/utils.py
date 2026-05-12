# Import standard library modules for base64 encoding, filesystem operations, regex, and retry delays
import base64
import os
import re
import time


# Define the verify_image_file function that checks if a filesystem path points to a valid image
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
    # Check if the path exists and points to a regular file
    if not os.path.isfile(image_path):
        # Return False if the path does not exist or is not a file
        return False

    # Import filetype for magic-byte detection (lazy import to avoid requiring it at module import time)
    import filetype
    # Infer the MIME type from the file's magic bytes
    mime_type = filetype.guess(image_path)

    # Validate that the detected file type is an image
    if not mime_type or not mime_type.mime.startswith("image/"):
        # Return False if the file is not an image
        return False

    # Return True if all validation checks pass
    return True


# Define the encode_image function that reads and base64-encodes an image file for API transmission
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
    # Open the image file in binary read mode
    with open(image_path, "rb") as image_file:
        # Read the entire file contents into memory
        binary_data = image_file.read()

        # Encode the binary data to base64 and decode to a UTF-8 string
        return base64.b64encode(binary_data).decode("utf-8")


# Define the sanitize_image_path function that generates an SEO-friendly filename from a description
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
    # Extract the absolute directory path from the original file path
    dir_path = os.path.abspath(os.path.dirname(image_path))

    # Extract and normalize the original file extension to lowercase
    extension = os.path.splitext(image_path)[1].lower()

    # Convert the AI-generated description to lowercase for consistency
    lower_content = image_content.lower()

    # Remove all non-alphabetic characters from the description
    clean_content = re.sub(r"[^a-z\s]+", " ", lower_content)

    # Replace whitespace sequences with hyphens and strip leading or trailing hyphens
    slug = re.sub(r"\s+", "-", clean_content).strip("-")

    # Join the directory path with the slug and original extension
    return os.path.join(dir_path, f"{slug}{extension}")


# Define the _guess_image_mime_type helper that detects image MIME type with JPEG fallback
def _guess_image_mime_type(image_path: str) -> str:
    """Return the detected image MIME type, falling back to JPEG."""
    # Import filetype for magic-byte detection (lazy import to avoid requiring it at module import time)
    import filetype
    # Guess the file type from the file's magic bytes
    kind = filetype.guess(image_path)
    # Check if the detected type is an image
    if kind and kind.mime.startswith("image/"):
        # Return the detected image MIME type
        return kind.mime

    # Fall back to JPEG if the file type could not be determined or is not an image
    return "image/jpeg"


# Set the maximum number of API retry attempts
_RETRY_MAX = 3
# Set the base value for exponential backoff calculation
_RETRY_BACKOFF_BASE = 2.0
# Set the API request timeout in seconds
_REQUEST_TIMEOUT = 30.0

# Set the Groq model ID for the Llama 4 Scout multimodal model
_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"


# Define the get_words function that sends an image to the Groq API and returns an AI description
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
    # Retrieve the Groq API key from the GROQ_API_KEY environment variable
    groq_api_key = os.getenv("GROQ_API_KEY")
    # Check if the API key is set
    if not groq_api_key:
        # Raise a RuntimeError with setup instructions for the API key
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it using: export GROQ_API_KEY='your-key-here' "
            "Get a free key at: https://console.groq.com/keys"
        )

    # Encode the image file to base64 for API transmission
    encoded_image = encode_image(image_path)
    # Guess the MIME type of the image for the data URL prefix
    image_mime_type = _guess_image_mime_type(image_path)

    # Set the correct label for singular or plural word count
    word_label = "word" if words == 1 else "words"

    # Build the request messages structure with the text prompt and image data URL
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

    # Build the full request payload with the model ID, temperature, and messages
    request_payload = {
        "model":       _MODEL_ID,
        "temperature": 2.0,
        "stream":      False,
        "stop":        None,
        "messages":    request_messages,
    }

    # Import the Groq client (lazy import to avoid requiring it at module import time)
    from groq import Groq
    # Create the Groq client with the API key and request timeout
    client = Groq(api_key=groq_api_key, timeout=_REQUEST_TIMEOUT)

    # Retry the API call up to the configured maximum number of times
    for attempt in range(1, _RETRY_MAX + 1):
        # Attempt the API call and catch any exceptions
        try:
            # Send the request payload to the Groq API for completion
            completion = client.chat.completions.create(**request_payload)

            # Check if the completion or its choices list is empty or None
            if not completion or not completion.choices:
                # Return an empty string if no valid response was received
                return ""
            # Check if the first choice has no message object
            if not completion.choices[0].message:
                # Return an empty string if the message is missing
                return ""
            # Check if the message content is empty or None
            if not completion.choices[0].message.content:
                # Return an empty string if the content is missing
                return ""

            # Return the AI-generated image description text
            return completion.choices[0].message.content

        # Catch any exception that occurs during the API call
        except Exception as exc:
            # Check if there are remaining retry attempts
            if attempt < _RETRY_MAX:
                # Calculate the exponential backoff delay for this attempt
                delay = _RETRY_BACKOFF_BASE ** attempt
                # Print the retry warning message to stderr
                print(
                    f"API call failed (attempt {attempt}/{_RETRY_MAX}), "
                    f"retrying in {delay:.1f}s: {exc}",
                    file=__import__("sys").stderr,
                )
                # Wait for the calculated backoff delay before retrying
                time.sleep(delay)
            # Handle the case when all retry attempts have been exhausted
            else:
                # Print the final failure message to stderr
                print(
                    f"API call failed after {_RETRY_MAX} attempts: {exc}",
                    file=__import__("sys").stderr,
                )

    # Return an empty string if all retry attempts were exhausted
    return ""
