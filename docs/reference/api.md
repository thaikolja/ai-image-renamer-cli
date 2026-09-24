# API Reference

Reference for the public Python API exposed by the package. The public functions are re-exported from the package root (`ai_image_renamer`).

## Public API

```python
from ai_image_renamer import (
    __version__,
    ImageRenamer,
    main,
    verify_image_file,
    encode_image,
    sanitize_image_path,
    get_words,
)
```

### `__version__`

The installed package version. Falls back to `1.5.0` when package metadata is unavailable (e.g. running from a source checkout).

### `verify_image_file(image_path: str) -> bool`

Determines whether the given path points to a valid image file.

Performs two validations:
1. The path exists and points to a regular file (not a directory or symlink)
2. The MIME type inferred from **magic bytes** (file header) starts with `image/`

Magic-byte detection prevents extension spoofing (e.g. a malicious `.exe` renamed to `image.jpg`).

**Returns** `True` if valid, `False` otherwise. Never raises.

### `encode_image(image_path: str) -> str`

Reads the binary contents of an image file and returns a base64-encoded string, suitable for embedding in API payloads.

**Raises** `FileNotFoundError`, `PermissionError`, or `OSError` on file access problems.

### `sanitize_image_path(image_path: str, image_content: str) -> str`

Generates a sanitized, SEO-friendly file path from a description:

1. Lowercases the content
2. Removes all non-alphabetic characters
3. Replaces whitespace sequences with single hyphens
4. Preserves the original directory and extension
5. Truncates at keyword boundaries (`MAX_FILENAME_LENGTH`)

Always returns an absolute path.

### `get_words(image_path, words=6, model=None, api_key=None, provider=None) -> str`

Generates a concise, SEO-friendly description for an image using the configured AI provider.

| Parameter | Type | Purpose |
|-----------|------|---------|
| `image_path` | `str` | Path to the image to analyze |
| `words` | `int` | Max words in the description (clamped to 1–50) |
| `model` | `str \| None` | Model override (takes priority over config) |
| `api_key` | `str \| None` | API key override (takes priority over env/config) |
| `provider` | `str \| None` | Provider override: `groq`, `ollama`, `openai` |

Provider resolution: CLI param → `PROVIDER` config key → `groq`.

**Returns** the description, or `""` on failure after retries.

**Raises**:
- `RuntimeError` if required credentials/endpoints are missing
- `ValueError` for an unknown provider
- `FileNotFoundError` if the image doesn't exist

### `ImageRenamer`

The rename pipeline orchestrator:

```python
class ImageRenamer:
    def __init__(self, args): ...   # starts rename() immediately
    def rename(self): ...
```

`args` is an `argparse.Namespace` with at least:
- `image_paths: list[str]`
- `words: int`
- `model`, `api_key`, `provider` (optional, default `None`)

The pipeline per image: verify → AI description → sanitize → dedupe → rename, with graceful skip/fail accounting and a final summary to stdout.

### `main()`

The CLI entry point. Parses `sys.argv`, expands glob patterns, caps at 3 images, and delegates to `ImageRenamer`. Registered as the `rename_images` console script.

## Internal modules

### `ai_image_renamer.config`

| Function | Description |
|----------|-------------|
| `config_path()` | `~/.config/ai-image-renamer-cli/.env`, or under `$XDG_CONFIG_HOME` when that variable is set |
| `get_config()` | Loads that file (auto-generates if missing), merges defaults, then applies exported environment variables, and caches the result |
| `load_environment()` | Loads the same file with `python-dotenv` without overriding variables already exported |
| `get(key, default=None)` | Convenience accessor for single config values |

Internal helpers: `config_dir()`, `ensure_config_file()`, `_parse_config_file()`, `_overlay_environment()`.

### `ai_image_renamer.utils` (private helpers)

| Function | Description |
|----------|-------------|
| `_get_words_groq(...)` | Groq-specific implementation of `get_words` |
| `_get_words_openai_compatible(...)` | OpenAI-compatible implementation (Ollama / generic endpoints) |
| `_build_request_messages(image_path, words)` | Encodes the image and builds the multimodal request messages |
| `_parse_temperature()` | Parses `TEMPERATURE`, falls back to `1.0` |
| `_parse_timeout()` | Parses `TIMEOUT`, falls back to `30.0` |
| `_parse_retries()` | Parses `MAX_RETRIES`, falls back to `3` |
| `_call_chat_completions(client, payload, retry_max)` | Calls the chat completions API with exponential backoff |
| `_extract_description(completion, words)` | Extracts and word-truncates the description from a completion |
| `_guess_image_mime_type(image_path)` | Detects MIME via magic bytes, falls back to `image/jpeg` |

### Retry behavior

API calls are retried up to `MAX_RETRIES` times (default 3) with exponential backoff (2s, 4s, 8s, …). Only *exceptions* trigger retries; an empty or `None` response is treated as a final failure. After all retries are exhausted, `get_words` returns `""` and the file is counted as failed.

### Word enforcement

The AI output is truncated to the requested word count regardless of the delimiter — hyphens, spaces, and other punctuation are all split points (`re.findall(r"[a-zA-Z]+", …)`), and only whole words are kept.
