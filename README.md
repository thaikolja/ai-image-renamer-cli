# AI Image Renamer

![PyPI-Version](https://img.shields.io/pypi/v/ai-image-renamer) ![PyPI - Downloads](https://img.shields.io/pypi/dm/ai-image-renamer) ![PyPI - License](https://img.shields.io/pypi/l/ai-image-renamer)

**AI Image Renamer CLI** is a command-line tool that uses AI vision models to rename image files based on their content, giving your photo collection more descriptive and searchable filenames. It works with **Groq's hosted API** (fast, free tier) or **local LLMs** (Ollama, LM Studio, vLLM, and any OpenAI-compatible endpoint) for fully offline renaming.

For Groq, [create your free API key here](https://console.groq.com/keys). **For full documentation, visit the [official docs](https://docs.kolja-nolte.com/ai-image-renamer-cli)**.

## Features

- 🤖 **AI:** Leverage the latest AI technology to quickly rename your images
- 🏠 **Local LLMs:** Run fully offline with [Ollama](https://ollama.com), LM Studio, vLLM, or any OpenAI-compatible endpoint
- ⚡️**Speed:** Groq's fast infrastructure processes your files in milliseconds
- 🔎 **SEO:** Generated file names are [SEO-friendly](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- 📚 **Batch:** Use up to 3 image files within a single command (processed sequentially)
- 👨‍💻 **Easy:** Renaming files requires only a single command line

## Table of Contents

[TOC]

## Installation

*AI Image Renamer* is available through multiple installation methods:

### 1. Using `pipx` (recommended)

```bash
# Install globally in an isolated environment (requires pipx installed)
pipx install ai-image-renamer

# With local LLM support (Ollama, LM Studio, etc.)
pipx install "ai-image-renamer[local]"
```

### 2. Using `pip`

```bash
# Install into the current Python environment
pip install ai-image-renamer

# With local LLM support (Ollama, LM Studio, etc.)
pip install "ai-image-renamer[local]"
```

### 3. From the Git repository

```bash
# Clone the repository
git clone https://gitlab.com/thaikolja/ai-image-renamer.git
# Navigate into the project directory
cd ai-image-renamer
# Install the package from source
pip install .
```

### 4. From a ZIP archive

1. Download the ZIP from the repository.
2. Extract it and run:

```bash
# Navigate into the extracted directory
cd ai-image-renamer-main
# Install the package from source
pip install .
```

### 5. Run directly from source

```bash
# Run via the module entry point without installation
python3 -m ai_image_renamer.cli path/to/image.jpg
```

After installation, obtain a free Groq API key. The recommended way to configure the tool is via a `config.ini` file in your working directory. On first run, a commented `config.ini` is auto-generated — just edit it to set your API key:

```ini
# Edit the generated config.ini
GROQ_API_KEY=gsk_your_api_key_here
```

Alternatively, set it as an environment variable:

```bash
export GROQ_API_KEY="your-key-here"
```

## Providers

The tool supports three AI backends, selected via `PROVIDER` in `config.ini` or the `--provider` CLI flag.

### Groq (default)

Hosted and fast. Requires a [free API key](https://console.groq.com/keys):

```ini
PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
```

### Ollama (local)

Fully offline. Your images never leave your machine:

```bash
# 1. Install Ollama: https://ollama.com
# 2. Start the server and pull a vision model
ollama serve
ollama pull llava
# 3. Install the CLI with local support
pip install "ai-image-renamer[local]"
```

```ini
PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434/v1
OLLAMA_MODEL=llava:latest
```

### OpenAI-compatible (LM Studio, vLLM, llama.cpp, ...)

Any server speaking the OpenAI Chat Completions API:

```ini
PROVIDER=openai
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_MODEL=my-vision-model
```

See the [documentation](https://docs.kolja-nolte.com/ai-image-renamer-cli/guide/providers) for full provider setup and troubleshooting.

## Usage

The `rename_images` command is your entry point to the tool. The AI model, word count, and other options are configurable via CLI flags or `config.ini`. Some limitations apply:

### Basic Usage

To rename a single image:

```bash
# Rename a single image file
rename_images path/to/your/image.jpg
```

To rename multiple images (up to 3 at once):

```bash
# Provide up to 3 image paths; append flags after paths
rename_images image1.png image2.jpg path/to/another/image.webp
```

Use shell glob patterns to select files:

```bash
# The shell expands the glob before passing paths to the tool
rename_images ~/Desktop/my-photos/*.png

# Match files containing a keyword in the name
rename_images ~/Photos/bangkok-*.jpg
```

To rename an image with only 3 words:

```bash
# Limit the generated filename to N words
rename_images -w 3 DSC_123.jpg
```

Override the API key, provider, or model for a single invocation:

```bash
# Override API key and model via CLI
rename_images --api-key gsk_xxx --model qwen/qwen3.6-27b

# Use a local Ollama model
rename_images --provider ollama photo.jpg

# Use a custom OpenAI-compatible endpoint
rename_images --provider openai --model my-vision-model photo.jpg
```

Use glob patterns to select files:

```bash
# The shell expands the glob before passing paths to the tool
rename_images ~/Desktop/my-photos/*.png
```

See `rename_images -h` for more options, or read the [documentation](https://docs.kolja-nolte.com/ai-image-renamer-cli/usage/options).

### Configuration

The tool reads settings from `./config.ini` in the current working directory. If the file doesn't exist, it is auto-generated with comments explaining every option:

```ini
# AI Image Renamer — Configuration
PROVIDER=groq                          # AI backend: groq, ollama, or openai
GROQ_API_KEY=                          # Your Groq API key (required for groq)
MODEL=qwen/qwen3.6-27b                 # Groq AI vision model (vision required)
OLLAMA_HOST=http://localhost:11434/v1  # Ollama endpoint (for ollama)
OLLAMA_MODEL=llava:latest              # Ollama vision model (for ollama)
OPENAI_API_BASE=                       # OpenAI-compatible endpoint (for openai)
OPENAI_API_KEY=                        # Key for the endpoint (for openai)
OPENAI_MODEL=                          # Model name (for openai)
TEMPERATURE=1.0                        # AI creativity (0.0 – 2.0)
TIMEOUT=30                             # API request timeout in seconds
MAX_RETRIES=3                          # Retries on API failure
DEFAULT_WORD_COUNT=6                   # Default word count (1 – 50)
MAX_FILENAME_LENGTH=100                # Max filename stem length (characters)
```

> [!IMPORTANT]
>
> CLI arguments (e.g. `-w`) always override the config file values.
>
> **Priority:** CLI flags → environment variables → `config.ini` → built-in defaults.

### Security

> [!WARNING]
>
> **Security:** Add `config.ini` to your `.gitignore` to avoid committing your API key.

### Limitations

The hosted Groq provider has the following practical limits to keep in mind (local providers like Ollama are not subject to these):

- **Image file size**: Each image must be **under 20 MB** (files larger than that will be rejected by the API).
- **Image resolution**: Very high-resolution photos (over 33 megapixels, e.g., some DSLR or smartphone camera shots) may need to be resized first.
- **Base64 limit**: When sending images via API, the base64-encoded data must stay under 4 MB.
- **Images per request**: The model accepts **up to 5 images at once** (the CLI caps this at 3 to stay well within bounds).
- **Model**: The model can be changed via `--model` CLI flag, `GROQ_MODEL` environment variable, or `MODEL` in `config.ini`. Browse available models at [console.groq.com/docs/models](https://console.groq.com/docs/models).
- **Model Reasoning**: Reasoning models (Qwen, GPT-OSS) output internal thinking by default. Set `REASONING_EFFORT=none` in `config.ini` to suppress it. See [Groq reasoning docs](https://console.groq.com/docs/reasoning) for details.

### Local LLM requirements

To use local providers, you need the `[local]` extra installed and a running server:

```bash
pip install "ai-image-renamer[local]"
```

Ollama users also need a vision model pulled (e.g., `ollama pull llava`) and the server running (`ollama serve`). Local models are typically slower than Groq but keep all images on your machine.

## Contributing

I welcome contributions to **AI Image Renamer**! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## Author

**Kolja Nolte** (kolja.nolte@gmail.com)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. A little self-promotion: If you're not sure which license to use for your project, check out https://whatlicense.org. 
