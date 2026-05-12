# AI Image Renamer

![PyPI-Version](https://img.shields.io/pypi/v/ai-image-renamer) ![PyPI - Downloads](https://img.shields.io/pypi/dm/ai-image-renamer) ![PyPI - License](https://img.shields.io/pypi/l/ai-image-renamer)

**AI Image Renamer CLI** is a command-line tool that uses generative AI to rename image files based on their content, giving your photo collection more descriptive and searchable filenames. A [**free** Groq API key](https://console.groq.com/keys) is required. **For full documentation, visit the [official docs](https://docs.kolja-nolte.com/ai-image-renamer-cli)**.

## Features

- 🤖 **AI:** Leverage the latest AI technology to quickly rename your images
- ⚡️**Speed:** Groq's fast infrastructure processes your files in milliseconds
- 🔎 **SEO:** Generated file names are [SEO-friendly](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- 📚 **Batch:** Use up to 3 image files within a single command (processed sequentially)
- 👨‍💻 **Easy:** Renaming files requires only a single command line



## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [1. Using pipx](#1-using-pipx-recommended)
  - [2. Using pip](#2-using-pip)
  - [3. From the Git repository](#3-from-the-git-repository)
  - [4. From a ZIP archive](#4-from-a-zip-archive)
  - [5. Run directly from source](#5-run-directly-from-source)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Limitations](#limitations)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)



## Installation

*AI Image Renamer* is available through multiple installation methods:

### 1. Using `pipx` (recommended)

```bash
# Install globally in an isolated environment (requires pipx installed)
pipx install ai-image-renamer
```

### 2. Using `pip`

```bash
# Install into the current Python environment
pip install ai-image-renamer
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
python -m ai_image_renamer.cli path/to/image.jpg
```

After installation, obtain a free Groq API key and set it as an environment variable:

```bash
# Set your Groq API key as an environment variable
export GROQ_API_KEY="your-key-here"
```

## Usage

The `rename-images` command is your entry point to the tool. However, since it's using [Groq and Meta's Llama 4 Scout](https://console.groq.com/docs/vision) model, some limitations apply:

### Basic Usage

To rename a single image:

```bash
# Rename a single image file
rename-images path/to/your/image.jpg
```

To rename multiple images (up to 3 at once):

```bash
# Provide up to 3 image paths; append flags after paths
rename-images image1.png image2.jpg path/to/another/image.webp
```

Use shell glob patterns to select files:

```bash
# The shell expands the glob before passing paths to the tool
rename-images ~/Desktop/my-photos/*.png
# Match files containing a keyword in the name
rename-images ~/Photos/bangkok-*.jpg
```

To rename an image with only 3 words:

```bash
# Limit the generated filename to N words
rename-images -w 3 DSC_123.jpg
```

See `rename-images -h` for more options, or read the [documentation](https://docs.kolja-nolte.com/ai-image-renamer-cli/usage/options).

### Limitations

This tool relies on Groq's hosted AI model, which has the following practical limits to keep in mind:

- **Image file size**: Each image must be **under 20 MB** (files larger than that will be rejected by the API).
- **Image resolution**: Very high-resolution photos (over 33 megapixels, e.g., some DSLR or smartphone camera shots) may need to be resized first.
- **Base64 limit**: When sending images via API, the base64-encoded data must stay under 4 MB.
- **Images per request**: The model accepts **up to 5 images at once** (the CLI caps this at 3 to stay well within bounds).
- **Preview model**: The Llama 4 Scout is still in preview, so it may change or be updated over time.

## Contributing

I welcome contributions to **AI Image Renamer**! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## Author

**Kolja Nolte** (kolja.nolte@gmail.com)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. A little self-promotion: If you're not sure which license to use for your project, check out https://whatlicense.org. 
