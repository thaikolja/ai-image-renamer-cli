#  AI Image Renamer
#
#  Copyright (C) 2026 Kolja Nolte
#  https://www.kolja-nolte.com
#  kolja.nolte@gmail.com
#
#  This work is licensed under the MIT License. You are free to use, modify, and distribute this work, provided that you include the copyright notice and this permission notice in all copies or substantial portions of the work. For more information, visit: https://opensource.org/licenses/MIT  # noqa: E501
#
#  @author      Kolja Nolte
#  @email       kolja.nolte@gmail.com
#  @license     MIT
#  @date        2026
#  @website     https://docs.kolja-nolte.com/ai-image-renamer
#  @repository  https://gitlab.com/thaikolja/ai-image-renamer

"""User configuration for AI Image Renamer.

Settings live in an editable ``.env`` file under the user config directory:

    $XDG_CONFIG_HOME/ai-image-renamer-cli/.env

When ``XDG_CONFIG_HOME`` is unset, that path is:

    ~/.config/ai-image-renamer-cli/.env

The file is created on first use and is not inside the pip or pipx install,
so edits survive upgrades. Command-line flags win, then exported environment
variables, then this file, then the built-in defaults.

A shell assignment such as ``GROQ_API_KEY=...`` in ``.zshrc`` is visible to
``echo`` but is not copied into child processes. Only ``export GROQ_API_KEY``
reaches this program.
"""

import os
import sys

# Directory and file name of the editable user config.
_APP_DIR_NAME = "ai-image-renamer-cli"
_CONFIG_FILE_NAME = ".env"

# The only Groq model that accepts images. Other Groq models are text-only.
GROQ_VISION_MODEL = "qwen/qwen3.8-27b"

# Hardcoded defaults — used when the user config omits a key and no env var is set.
_DEFAULTS = {
    "PROVIDER": "groq",
    "GROQ_API_KEY": "",
    "MODEL": GROQ_VISION_MODEL,
    "OLLAMA_HOST": "http://localhost:11434/v1",
    "OLLAMA_MODEL": "llava:latest",
    "OPENAI_API_BASE": "",
    "OPENAI_API_KEY": "",
    "OPENAI_MODEL": "",
    "TEMPERATURE": "1.0",
    "TIMEOUT": "30",
    "MAX_RETRIES": "3",
    "DEFAULT_WORD_COUNT": "6",
    "MAX_FILENAME_LENGTH": "100",
    "REASONING_EFFORT": "none",
}

# Exported process environment variables that override the config file.
# GROQ_MODEL overrides MODEL; the other names match their config keys.
_ENV_OVERRIDES = (
    ("GROQ_API_KEY", "GROQ_API_KEY"),
    ("GROQ_MODEL", "MODEL"),
    ("OPENAI_API_KEY", "OPENAI_API_KEY"),
)

# Module-level cache; populated on the first get_config() call.
_config = None

# Template written when the user config file does not exist yet.
_TEMPLATE = """# AI Image Renamer configuration
#
# This file stores the model, word count, and other defaults.
# Edit it in place. pip and pipx reinstalls do not replace it.
#
# Priority: command-line flags, then exported environment variables,
# then this file, then built-in defaults.
#
# A shell profile must export a variable for this program to see it.
# `GROQ_API_KEY=...` in .zshrc is visible to `echo` but is not inherited.
# Use `export GROQ_API_KEY="your-key-here"`. An exported value overrides
# the same key below.

# Which AI backend to use: groq, ollama, or openai
# - groq:   hosted Groq API (requires GROQ_API_KEY)
# - ollama: local Ollama server (see https://ollama.com)
# - openai: any OpenAI-compatible endpoint (LM Studio, vLLM, llama.cpp, ...)
PROVIDER=groq

# Your Groq API key (required for PROVIDER=groq)
# Get a free key at: https://console.groq.com/keys
GROQ_API_KEY=

# Groq model. Only qwen/qwen3.8-27b accepts images.
# https://console.groq.com/docs/model/qwen/qwen3.8-27b
MODEL=qwen/qwen3.8-27b

# Ollama server (OpenAI-compatible endpoint, required for PROVIDER=ollama)
# Start it with: ollama serve
OLLAMA_HOST=http://localhost:11434/v1

# The Ollama vision model to use for image analysis
# Pull a model first, e.g.: ollama pull llava
OLLAMA_MODEL=llava:latest

# OpenAI-compatible endpoint (required for PROVIDER=openai)
# e.g. http://localhost:1234/v1 for LM Studio, http://localhost:8000/v1 for vLLM
OPENAI_API_BASE=

# API key for the OpenAI-compatible endpoint (if required)
OPENAI_API_KEY=

# Model name for the OpenAI-compatible endpoint
OPENAI_MODEL=

# Creativity / randomness of the AI output (0.0 – 2.0)
TEMPERATURE=1.0

# API request timeout in seconds
TIMEOUT=30

# How many times to retry a failed API call
MAX_RETRIES=3

# Default word count for generated filenames (1 – 50)
DEFAULT_WORD_COUNT=6

# Maximum length of the generated filename stem (characters)
MAX_FILENAME_LENGTH=100

# Reasoning effort: "none" disables reasoning (keep model output concise)
# Only for Qwen and GPT-OSS models. Options: none, default, low, medium, high
# See https://console.groq.com/docs/reasoning
REASONING_EFFORT=none
"""


def config_dir():
    """Return the user config directory, creating nothing.

    ``$XDG_CONFIG_HOME/ai-image-renamer-cli`` when that variable is set,
    otherwise ``~/.config/ai-image-renamer-cli``.
    """
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    if xdg:
        base = xdg
    else:
        base = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, _APP_DIR_NAME)


def config_path():
    """Return the path to the editable user config file."""
    return os.path.join(config_dir(), _CONFIG_FILE_NAME)


def clear_cache():
    """Drop the cached settings so the next read uses the filesystem."""
    global _config
    _config = None


def ensure_config_file():
    """Create the user config directory and template file when missing.

    The directory is mode ``0700`` and the file is mode ``0600``.
    An existing file is left unchanged.
    """
    directory = config_dir()
    path = config_path()
    try:
        os.makedirs(directory, exist_ok=True)
        os.chmod(directory, 0o700)
    except OSError as exc:
        print(f"Warning: could not create config directory at {directory}: {exc}", file=sys.stderr)
        return path

    if os.path.isfile(path):
        return path

    temporary = path + ".tmp"
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(_TEMPLATE)
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    except OSError as exc:
        print(f"Warning: could not create config at {path}: {exc}", file=sys.stderr)
        return path

    print(f"Created default config at {path}", file=sys.stderr)
    return path


def load_environment():
    """Load the user config file without replacing existing variables.

    Exported variables such as ``GROQ_API_KEY`` stay as they are. Keys that
    are missing from the process environment are filled from the config file.
    Returns the config path.
    """
    path = ensure_config_file()
    from dotenv import load_dotenv

    # override=False is required. The generated file contains GROQ_API_KEY=
    # and must not wipe a key already exported by the shell.
    load_dotenv(dotenv_path=path, override=False)
    return path


def _parse_config_file(path):
    """Parse the user config file and return a dict of string values.

    Blank lines and ``#`` comments are ignored. ``export KEY=value`` and
    surrounding quotes are accepted, matching ``.env`` syntax.
    """
    if not os.path.isfile(path):
        return {}

    from dotenv import dotenv_values

    try:
        parsed = dotenv_values(path)
    except OSError as exc:
        print(f"Warning: could not read config at {path}: {exc}", file=sys.stderr)
        return {}

    config = {}
    for key, value in parsed.items():
        if not key:
            continue
        config[key] = "" if value is None else value
    return config


def _overlay_environment(merged):
    """Let exported environment variables replace file values."""
    for env_name, key in _ENV_OVERRIDES:
        value = (os.environ.get(env_name) or "").strip()
        if value:
            merged[key] = value


def get_config():
    """Load the user config file and return the merged settings.

    The file is created on first call when it is missing. The result is
    cached. Call ``clear_cache()`` after changing the file or the process
    environment in the same process.
    """
    global _config
    if _config is not None:
        return _config

    path = ensure_config_file()
    merged = dict(_DEFAULTS)
    merged.update(_parse_config_file(path))
    _overlay_environment(merged)
    _config = merged
    return _config


def get(key, default=None):
    """Return a config value by key, falling back to ``default``."""
    return get_config().get(key, default)
