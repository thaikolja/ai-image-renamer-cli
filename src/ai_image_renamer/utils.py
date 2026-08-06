"""Utility functions for image validation, encoding, and AI API calls."""

import base64
import os
import re
import sys
import time
from typing import Any, Optional

# Import package config module for user-defined settings
from . import config


# Define the verify_image_file function that checks if a filesystem path points to a valid image
def verify_image_file(image_path: str) -> bool:
    """Determine whether the given filesystem path points to a valid image file.

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

    # Import filetype for magic-byte detection (lazy import
    # to avoid requiring it at module import time)
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
    """Read the binary contents of an image file and return a base64-encoded string.

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
    """Generate a sanitized, SEO-friendly file path from image description.

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
             Truncates at keyword boundaries when possible; a single very long
             keyword is kept intact rather than being cut mid-word.

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

    # Read maximum filename stem length from config (default 100)
    max_len_raw = config.get("MAX_FILENAME_LENGTH", "100")
    try:
        max_len = int(max_len_raw)
    except (ValueError, TypeError):
        max_len = 100

    # Truncate at a keyword boundary when possible, but never cut a keyword in half.
    if len(slug) > max_len:
        boundary = slug.rfind("-", 0, max_len + 1)
        if boundary > 0:
            slug = slug[:boundary]

    # Join the directory path with the slug and original extension
    return os.path.join(dir_path, f"{slug}{extension}")


# Define the _guess_image_mime_type helper that detects image MIME type with JPEG fallback
def _guess_image_mime_type(image_path: str) -> str:
    """Return the detected image MIME type, falling back to JPEG."""
    # Import filetype for magic-byte detection (lazy import
    # to avoid requiring it at module import time)
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

# Providers handled by the OpenAI-compatible code path
_OPENAI_COMPATIBLE_PROVIDERS = ("ollama", "openai")


# Define the get_words dispatcher that routes to the configured AI provider
def get_words(
    image_path: str,
    words: int = 6,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
) -> str:
    """Generate a concise, SEO-friendly description for an image using AI.

    Sends an image to the configured AI provider and receives a short text
    description suitable for use as a filename.

    Supported providers:
    - "groq": hosted Groq API (requires GROQ_API_KEY)
    - "ollama": local Ollama server via its OpenAI-compatible endpoint
    - "openai": any OpenAI-compatible endpoint (LM Studio, vLLM, llama.cpp, ...)

    The provider, model, temperature, timeout, and retry count are read from
    config.ini (with hardcoded fallbacks). Includes automatic retry with
    exponential backoff for transient failures.

    Args:
        image_path: Filesystem path to the image to analyze.
        words: Maximum number of words requested in the description (1-50).
        model: Optional CLI override for the model (takes priority over
               config.ini and hardcoded default).
        api_key: Optional CLI override for the API key (takes priority
                 over environment variable and config.ini).
        provider: Optional CLI override for the provider ("groq", "ollama",
                  or "openai"). Takes priority over config.ini.

    Returns:
        AI-generated description, or empty string on failure after retries.

    Raises:
        RuntimeError: If required credentials/endpoints are not configured.
        ValueError: If an unknown provider is given.
        FileNotFoundError: If image_path does not exist.

    """
    # Provider priority: CLI param → config.ini
    provider = provider or config.get("PROVIDER", "groq")

    # Dispatch to the provider-specific implementation
    if provider == "groq":
        return _get_words_groq(image_path, words, model, api_key)
    if provider in _OPENAI_COMPATIBLE_PROVIDERS:
        return _get_words_openai_compatible(image_path, words, model, api_key, provider)
    raise ValueError(f"Unknown provider '{provider}'. Choose from: groq, ollama, openai")


def _get_words_groq(
    image_path: str,
    words: int,
    model: Optional[str],
    api_key: Optional[str],
) -> str:
    """Send the image to the Groq API and return an AI description."""
    # API key priority: CLI param → env var → config.ini
    groq_api_key = api_key or os.getenv("GROQ_API_KEY") or config.get("GROQ_API_KEY")
    # Check if the API key is set
    if not groq_api_key:
        # Raise a RuntimeError with setup instructions for the API key
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Pass --api-key, or export GROQ_API_KEY, or set it in ./config.ini. "
            "Get a free key at: https://console.groq.com/keys"
        )

    # Clamp word count to valid range as a safety net
    words = max(1, min(50, words))

    # Build the shared multimodal request messages
    request_messages = _build_request_messages(image_path, words)

    # Model priority: CLI param → GROQ_MODEL env var → config.ini
    effective_model = model or os.getenv("GROQ_MODEL") or config.get("MODEL")

    # Only include reasoning_effort for reasoning models (Qwen, GPT-OSS)
    reasoning_effort: Optional[str] = config.get("REASONING_EFFORT")
    if not (reasoning_effort and effective_model and ("qwen" in effective_model or "gpt-oss" in effective_model)):
        reasoning_effort = None

    request_payload = {
        "model": effective_model,
        "temperature": _parse_temperature(),
        "reasoning_effort": reasoning_effort,
        "stream": False,
        "stop": None,
        "messages": request_messages,
    }

    # Import the Groq client (lazy import to avoid requiring it at module import time)
    from groq import Groq

    # Create the Groq client with the API key and config-driven request timeout
    client = Groq(api_key=groq_api_key, timeout=_parse_timeout())

    # Call the API with retries and extract the description
    completion = _call_chat_completions(client, request_payload, _parse_retries())
    return _extract_description(completion, words)


def _get_words_openai_compatible(
    image_path: str,
    words: int,
    model: Optional[str],
    api_key: Optional[str],
    provider: str,
) -> str:
    """Send the image to an OpenAI-compatible endpoint (Ollama, LM Studio, ...)."""
    # Clamp word count to valid range as a safety net
    words = max(1, min(50, words))

    # Resolve the endpoint, model, and API key for the chosen provider
    if provider == "ollama":
        base_url = config.get("OLLAMA_HOST", "http://localhost:11434/v1")
        effective_model = model or config.get("OLLAMA_MODEL", "llava:latest")
        effective_api_key = api_key or "ollama"
    else:
        base_url = config.get("OPENAI_API_BASE", "")
        effective_model = model or config.get("OPENAI_MODEL", "")
        effective_api_key = api_key or os.getenv("OPENAI_API_KEY") or config.get("OPENAI_API_KEY") or "local"

    # Validate the required endpoint and model settings
    if not base_url:
        raise RuntimeError(
            "OPENAI_API_BASE is not set. "
            "Set OPENAI_API_BASE in ./config.ini (e.g. "
            "OPENAI_API_BASE=http://localhost:1234/v1 for LM Studio)."
        )
    if not effective_model:
        raise RuntimeError("OPENAI_MODEL is not set. Pass --model, or set OPENAI_MODEL in ./config.ini.")

    # Import the OpenAI client (lazy import; requires the [local] extra)
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "The 'openai' package is required for local LLM providers. "
            'Install it with: pip install "ai-image-renamer[local]"'
        )

    # Build the shared multimodal request messages
    request_messages = _build_request_messages(image_path, words)

    request_payload = {
        "model": effective_model,
        "temperature": _parse_temperature(),
        "messages": request_messages,
    }

    # Create the OpenAI-compatible client with the endpoint and timeout
    client = OpenAI(api_key=effective_api_key, base_url=base_url, timeout=_parse_timeout())

    # Call the API with retries and extract the description
    completion = _call_chat_completions(client, request_payload, _parse_retries())
    return _extract_description(completion, words)


def _build_request_messages(image_path: str, words: int) -> list:
    """Encode the image and build the multimodal request messages."""
    # Encode the image file to base64 for API transmission
    encoded_image = encode_image(image_path)
    # Guess the MIME type of the image for the data URL prefix
    image_mime_type = _guess_image_mime_type(image_path)

    # Set the correct label for singular or plural word count
    word_label = "word" if words == 1 else "words"

    # Build the request messages structure with the text prompt and image data URL
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "What is visible in this image? "
                        f"List only the main objects, people, or scene "
                        f"using no more than {words} {word_label}. "
                        "Separate each keyword with a hyphen. "
                        "Output nothing else."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{image_mime_type};base64,{encoded_image}"},
                },
            ],
        }
    ]


def _parse_temperature() -> float:
    """Parse TEMPERATURE from config.ini, falling back to 1.0."""
    _temp_raw = config.get("TEMPERATURE", "1.0")
    try:
        return float(_temp_raw)
    except (ValueError, TypeError):
        print(
            f"Invalid TEMPERATURE '{_temp_raw}' in config.ini. Using 1.0.",
            file=sys.stderr,
        )
        return 1.0


def _parse_timeout() -> float:
    """Parse TIMEOUT from config.ini, falling back to the module default."""
    _timeout_raw = config.get("TIMEOUT", str(_REQUEST_TIMEOUT))
    try:
        return float(_timeout_raw)
    except (ValueError, TypeError):
        print(
            f"Invalid TIMEOUT '{_timeout_raw}' in config.ini. Using {_REQUEST_TIMEOUT}.",
            file=sys.stderr,
        )
        return _REQUEST_TIMEOUT


def _parse_retries() -> int:
    """Parse MAX_RETRIES from config.ini, falling back to the module default."""
    _retries_raw = config.get("MAX_RETRIES", str(_RETRY_MAX))
    try:
        return int(_retries_raw)
    except (ValueError, TypeError):
        print(
            f"Invalid MAX_RETRIES '{_retries_raw}' in config.ini. Using {_RETRY_MAX}.",
            file=sys.stderr,
        )
        return _RETRY_MAX


def _call_chat_completions(client: Any, request_payload: dict, retry_max: int) -> Any:
    """Call the chat completions API, retrying with exponential backoff.

    Returns the raw completion object, or None if all retries were exhausted.
    """
    for attempt in range(1, retry_max + 1):
        # Attempt the API call and catch any exceptions
        try:
            # Send the request payload to the API for completion
            return client.chat.completions.create(**request_payload)
        except Exception as exc:
            # Check if there are remaining retry attempts
            if attempt < retry_max:
                # Calculate the exponential backoff delay for this attempt
                delay = _RETRY_BACKOFF_BASE**attempt
                # Print the retry warning message to stderr
                print(
                    f"API call failed (attempt {attempt}/{retry_max}), retrying in {delay:.1f}s: {exc}",
                    file=sys.stderr,
                )
                # Wait for the calculated backoff delay before retrying
                time.sleep(delay)
            else:
                # Print the final failure message to stderr
                print(
                    f"API call failed after {retry_max} attempts: {exc}",
                    file=sys.stderr,
                )

    # Return None if all retry attempts were exhausted
    return None


def _extract_description(completion: Any, words: int) -> str:
    """Extract the AI description from a completion and enforce the word limit."""
    # Check if the completion or its choices list is empty or None
    if not completion or not completion.choices:
        return ""
    # Check if the first choice has no message object
    if not completion.choices[0].message:
        return ""
    # Check if the message content is empty or None
    if not completion.choices[0].message.content:
        return ""

    # Get the AI-generated description and enforce the word limit
    # (splitting by any non-alphabetic character)
    description = completion.choices[0].message.content.strip()
    desc_words = re.findall(r"[a-zA-Z]+", description)
    if len(desc_words) > words:
        description = " ".join(desc_words[:words])
    return description
