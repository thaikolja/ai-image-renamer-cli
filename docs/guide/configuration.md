# Configuration

AI Image Renamer is configured through an editable `.env` file in your user config directory:

```text
~/.config/ai-image-renamer-cli/.env
```

When `XDG_CONFIG_HOME` is set, the file is `$XDG_CONFIG_HOME/ai-image-renamer-cli/.env` instead. The install location used by pip or pipx does not contain this file, so upgrades do not replace your settings.

## How configuration works

1. On first run, a commented `.env` is **auto-generated** in that directory (mode `0600`)
2. You edit it to set your preferences
3. Values are read on every invocation

**Priority order** (highest wins):

```
CLI flags → exported environment variables → user config file → built-in defaults
```

::: warning
CLI arguments (e.g. `-w 3`) always override config file values.
:::

::: danger Security
The file lives outside the repository and can hold your API key. It is created so only your user can read it. Do not commit a copy.
:::

## Environment variables

Some values can also be set via environment variables:

| Variable | Overrides | Notes |
|----------|-----------|-------|
| `GROQ_API_KEY` | `GROQ_API_KEY` in config | Used by the `groq` provider |
| `GROQ_MODEL` | `MODEL` in config | Used by the `groq` provider |
| `OPENAI_API_KEY` | `OPENAI_API_KEY` in config | Used by the `openai` provider |

Export variables from your shell profile. A line like `GROQ_API_KEY=...` in `.zshrc` is visible to `echo` and is not inherited by the program; use `export GROQ_API_KEY=...`. The user config file is also loaded with `python-dotenv`, and it does not replace variables that are already exported.

## Full config reference

```ini
# AI Image Renamer — Configuration

# Which AI backend to use: groq, ollama, or openai
PROVIDER=groq

# Your Groq API key (required for PROVIDER=groq)
GROQ_API_KEY=

# The Groq model to use for image analysis
MODEL=qwen/qwen3.8-27b

# Ollama server (OpenAI-compatible endpoint)
OLLAMA_HOST=http://localhost:11434/v1

# The Ollama vision model to use for image analysis
OLLAMA_MODEL=llava:latest

# OpenAI-compatible endpoint (required for PROVIDER=openai)
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
REASONING_EFFORT=none
```

## Key details

### `PROVIDER`
The AI backend. `groq`, `ollama`, or `openai`. See the [Providers guide](/guide/providers).

### `MODEL`
Groq model id. Only [`qwen/qwen3.8-27b`](https://console.groq.com/docs/model/qwen/qwen3.8-27b) accepts images. The default is that id. A different Groq model prints a warning and cannot describe a picture. This key is read from `~/.config/ai-image-renamer-cli/.env`.

### `TEMPERATURE`
Controls output randomness (0.0 – 2.0). Lower values produce more deterministic, focused keywords; higher values produce more varied descriptions. Default `1.0`.

### `MAX_RETRIES`
How many times a failed API call is retried before the image is skipped. Retries use exponential backoff (2s, 4s, 8s, …). Default `3`.

### `DEFAULT_WORD_COUNT`
Default number of words in generated filenames. Overridable per invocation with `-w`. Default `6`.

### `MAX_FILENAME_LENGTH`
Maximum length of the filename stem (without extension). Truncation happens at keyword boundaries — keywords are never cut in half. Default `100`.

### `REASONING_EFFORT`
Only applies to reasoning models (Qwen, GPT-OSS) on Groq. Setting `none` suppresses internal chain-of-thought output, keeping responses concise. Options: `none`, `default`, `low`, `medium`, `high`. See the [Groq reasoning docs](https://console.groq.com/docs/reasoning).

## Auto-generated template

The generated `.env` file is written by the package itself. If you delete it, a fresh commented template is created on the next run. The template always reflects the newest options, so it's safe to regenerate and diff. A `config.ini` in the working directory is not read.
