# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1

### v1.3.0

#### Added

* **Config File:** New `config.ini` at the project root for user configuration (API key, model, temperature, timeout, retries, word count). Auto-generated with comments on first run if missing.
* **Config Module:** New `src/ai_image_renamer/config.py` for config loading, merging, and auto-generation
* **CLI Flags:** Added `--api-key` and `--model` CLI arguments to override config values per invocation
* **Priority Chain:** Settings now follow a clear priority: CLI arguments → environment variables → `config.ini` → hardcoded defaults
* **Glob Expansion:** Image paths containing wildcards (`*`, `?`, `[`) are now expanded via `glob.glob()` before processing
* **Config Settings:** Added `MAX_FILENAME_LENGTH` (100) and `REASONING_EFFORT` (none) to `config.ini` for filename length capping and reasoning suppression
* **Word Enforcement:** AI output is post-processed to enforce the requested word count, splitting on any non-alphabetic delimiter
* **Keyword Boundaries:** Filename truncation now stops at keyword boundaries; keywords are never cut in half
* **Config Validation:** Numeric config values (`DEFAULT_WORD_COUNT`, `TEMPERATURE`, `TIMEOUT`, `MAX_RETRIES`, `MAX_FILENAME_LENGTH`) are validated with clear error messages and fallbacks
* **`.gitignore`:** Added `config.ini` to `.gitignore` to prevent accidental API key commits

#### Changed

* **API Key:** `GROQ_API_KEY` is now read from `config.ini` first, with environment variable as fallback (was environment-only)
* **Model:** The Groq model is now configurable via `--model` CLI flag, `GROQ_MODEL` env var, or `MODEL` in `config.ini` (was hardcoded)
* **Temperature / Timeout / Retries:** Now read from `config.ini` rather than hardcoded module constants
* **Temperature Default:** Lowered from `2.0` to `1.0` in template to reduce incoherent/rambling outputs
* **AI Prompt:** Rewritten to ask "What is visible in this image?" with explicit instruction to list keywords and output nothing else
* **Reasoning Suppression:** Replaced `reasoning_format` with `reasoning_effort: "none"` to silence model thinking tokens (correct parameter for Qwen models)
* **Word Count Default:** `--words` default now comes from `config.ini` `DEFAULT_WORD_COUNT` (falls back to 6)
* **`get_words()`:** Accepts optional `model` and `api_key` keyword arguments for CLI overrides; returns text truncated to word count regardless of delimiter
* **`sanitize_image_path()`:** Truncates at keyword boundaries; a single long keyword is kept intact rather than cut mid-word
* **CLI Limit Message:** Improved truncation warning now shows which files are processed and which are skipped
* **Tests:** Updated test mocks to use `config.get` for API-calling tests; fixed missing-key test to mock config; added tests for word truncation, keyword-boundary truncation, and long keyword preservation
* **Docs:** Updated `README.md`, `AGENTS.md`, and all module docstrings to reference `config.ini`, new CLI flags, word enforcement, and reasoning suppression

#### Removed

* **Global Config:** Dropped `~/.config/ai-image-renamer/` global config directory; only `./config.ini` is used now

### v1.2.0

#### Added

* **Table of Contents:** Added manual TOC to README.md with links to all sections
* **Limitations Section:** Documented Groq API limits (file size, resolution, base64, preview status) in layman's terms
* **Mock Module Pre-registration:** Tests now pre-register mock `filetype` and `groq` modules, so all 30 tests pass without any third-party deps installed
* **Retry Logic:** API calls now retry up to 3 times with exponential backoff for transient failures
* **Timeout:** Added 30-second request timeout to prevent hanging on stalled connections
* **Batch Summary:** Processing now prints a summary of results (renamed, skipped, failed counts)
* **Grammar Fix:** Singular/plural "word" correction in API prompt

#### Changed

* **AGENTS.md:** Translated from Chinese to English; updated project structure, model name (Scout), CLI cap (3 images), dedup logic, and added CI/CD section
* **README.md:** Reworded for accuracy and grammar; added `#` one-liner comments to every statement in code blocks
* **Lazy Imports:** Moved `import filetype`, `from groq import Groq`, and `from dotenv import load_dotenv` inside the functions that use them, allowing the package to be imported without third-party deps
* **Test Patches:** Changed `@patch` targets from module-level aliases (`ai_image_renamer.utils.filetype.guess`) to original module paths (`filetype.guess`) to match lazy import structure
* **Image Limit:** CLI now caps processing at 3 images per invocation (down from unlimited)
* **Output Destinations:** Progress messages now go to stderr; only the summary goes to stdout
* **Message Construction:** Replaced fragile `json.loads(f-string)` with native Python data structures (security improvement)
* **Model Reference:** Updated all docstrings from Llama 4 Maverick to Llama 4 Scout

#### Fixed

* Module collection errors when running pytest without third-party dependencies installed (26 tests now pass without deps, 0 before)
* Duplicate copyright block in `test_cli.py` left by previous automation
* JSON injection risk in API request payload construction
* Misleading model name in package-level docstring

### v1.1.0

#### Changed

* **Model Update:** Replaced the **deprecated Meta Llama 4 Maverick with the Llama 4 Scout** model for better performance and stability
* **Import Paths:** Fixed relative imports in `renamer.py` for better package compatibility
* **Documentation:** Added comprehensive inline comments and docstrings throughout all modules:
  - `utils.py`: Detailed function documentation with Args, Returns, Raises, Examples, and Notes
  - `renamer.py`: Step-by-step pipeline documentation and class/method docstrings
  - `cli.py`: Complete CLI argument documentation and usage examples
  - `__init__.py`: Package-level documentation and public API exports

#### Added

* **main.py:** New entry point in project root directory for easy development usage
* **Public API:** Defined `__all__` in `__init__.py` for clean package exports
* **Version Info:** Added `__version__` to package for programmatic version access
* **Test Improvements:** Enhanced test files with better import handling and documentation

#### Fixed

* Import path issues when running from the development environment
* Test imports now work in both installed and development environments

### v1.0.0

#### Added

* Initial release of the *AI Image Renamer* CLI tool
