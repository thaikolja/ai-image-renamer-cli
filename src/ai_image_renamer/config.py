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

"""Configuration management for AI Image Renamer.

Reads a config.ini file from the current working directory.
If none exists, a commented template is auto-generated so users
can see all available options immediately.

CLI arguments (e.g. -w) always override config values.
"""

import os
import sys

# Hardcoded defaults — used when no config.ini exists and no env var is set
_DEFAULTS = {
    "PROVIDER": "groq",
    "GROQ_API_KEY": "",
    "MODEL": "qwen/qwen3.6-27b",
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

# Module-level cache; populated on first get_config() call
_config = None

# Template written when no config.ini is found
_TEMPLATE = """# AI Image Renamer — Configuration
#
# This file sets defaults for rename_images commands.
# CLI arguments (e.g. -w) always override these defaults.

# Which AI backend to use: groq, ollama, or openai
# - groq:   hosted Groq API (requires GROQ_API_KEY)
# - ollama: local Ollama server (see https://ollama.com)
# - openai: any OpenAI-compatible endpoint (LM Studio, vLLM, llama.cpp, ...)
PROVIDER=groq

# Your Groq API key (required for PROVIDER=groq)
# Get a free key at: https://console.groq.com/keys
GROQ_API_KEY=

# The Groq model to use for image analysis
# Browse available models: https://console.groq.com/docs/models
MODEL=qwen/qwen3.6-27b

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


def _get_config_path():
    """Return the path to config.ini in the current working directory."""
    return os.path.join(os.getcwd(), "config.ini")


def _generate_config():
    """Create a commented config.ini in the CWD if none exists.

    Prints a message to stderr so the user knows the file was created.
    """
    path = _get_config_path()
    if os.path.exists(path):
        return

    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_TEMPLATE)
        print(f"Created default config at {path}", file=sys.stderr)
    except OSError as exc:
        print(f"Warning: could not create config.ini at {path}: {exc}", file=sys.stderr)


def _parse_config_file(path):
    """Parse a key=value config.ini file and return a dict.

    Lines starting with # are treated as comments.
    Lines starting with [ are treated as section headers (ignored).
    Blank lines are ignored.
    Keys and values are stripped of surrounding whitespace.
    """
    config = {}
    if not os.path.isfile(path):
        return config

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("["):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    return config


def get_config():
    """Load config.ini from CWD and return a merged dict.

    Auto-generates a commented config.ini on first call if none exists.
    The result is cached so subsequent calls return the same dict.
    """
    global _config
    if _config is not None:
        return _config

    # Auto-generate config.ini if missing
    _generate_config()

    _config = dict(_DEFAULTS)
    file_cfg = _parse_config_file(_get_config_path())
    _config.update(file_cfg)

    return _config


def get(key, default=None):
    """Return a config value by key, falling back to default."""
    return get_config().get(key, default)
