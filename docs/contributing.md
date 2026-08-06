# Contributing

Thank you for considering contributing to AI Image Renamer! This document outlines the development workflow.

## Development setup

```bash
# Clone the repository
git clone https://github.com/thaikolja/ai-image-renamer.git
cd ai-image-renamer

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install the package in editable mode with all extras
pip install -e ".[local,test,ci]"
```

## Branching workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run the checks (below)
5. Commit with a [Conventional Commit](https://www.conventionalcommits.org/) message
6. Push and open a pull request

## Code style

- Follows [PEP 8](https://peps.python.org/pep-0008/)
- UTF-8 encoding, copyright header in every source file
- Google-style docstrings for functions and classes
- `snake_case` for variables/functions, `PascalCase` for classes

## Commit conventions

Follows [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix a bug
docs: update documentation
test: add/modify tests
refactor: refactor code
```

## Quality checks

Run all three before submitting:

```bash
# Lint
ruff check src/

# Format check
ruff format --check src/

# Type check
mypy src/

# Tests
pytest
```

## Testing conventions

- Framework: `unittest` with `unittest.mock` (no pytest fixtures — pure unittest style)
- Class naming: `Test<ModuleName>`
- Method naming: `test_<function>_<scenario>`
- All external dependencies (Groq API, OpenAI API, filesystem) are mocked
- Real test images live in `assets/` and are used only when present (otherwise tests skip)
- Imports use try/except to handle both installed and dev environments

## Documentation

When you change behavior, update:

1. The relevant docs page under `docs/`
2. `CHANGELOG.md` (Keep a Changelog format)
3. The auto-generated config template in `src/ai_image_renamer/config.py` if you add config keys

## Reporting bugs

Open an issue with:

- The exact command you ran
- Your `config.ini` (with the API key redacted!)
- The provider and model used
- Full error output

## Feature requests

Open an issue describing the feature, its use case, and how it fits the existing architecture.
