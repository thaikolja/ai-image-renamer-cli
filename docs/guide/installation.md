# Installation

*AI Image Renamer* supports Python 3.8+ and is available through several installation methods.

## 1. Using `pipx` (recommended)

Installs the tool globally in an isolated environment, so it never conflicts with your other Python packages:

```bash
pipx install ai-image-renamer
```

To install with local LLM support:

```bash
pipx install "ai-image-renamer[local]"
```

## 2. Using `pip`

Installs into the current Python environment:

```bash
pip install ai-image-renamer
```

With the `local` extra (required for Ollama / OpenAI-compatible providers):

```bash
pip install "ai-image-renamer[local]"
```

## 3. From the Git repository

```bash
git clone https://github.com/thaikolja/ai-image-renamer.git
cd ai-image-renamer
pip install .
```

Editable (dev) install:

```bash
pip install -e .
```

Install with all extras for development:

```bash
pip install -e ".[local,test,ci]"
```

## 4. From a ZIP archive

Download the ZIP from the repository, extract it, and run:

```bash
cd ai-image-renamer-main
pip install .
```

## 5. Run directly from source

No installation needed — clone the repo and run the module entry point:

```bash
python3 -m ai_image_renamer.cli path/to/image.jpg
```

## 6. Development environment

For contributors:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install the package in editable mode with all extras
pip install -e ".[local,test,ci]"

# Run the tests
pytest

# Run lint and type checks
ruff check src/
mypy src/
```

## Optional extras

| Extra | Packages | When you need it |
|-------|----------|------------------|
| `local` | `openai>=1.0.0` | Ollama, LM Studio, vLLM, or any OpenAI-compatible provider |
| `test` | `pytest` | Running the test suite |
| `ci` | `pytest`, `ruff`, `mypy` | Linting and type checking (used by CI) |

## Verification

After installation, verify everything works:

```bash
rename_images --version
```

You should see:

```
rename_images 1.5.0
```
