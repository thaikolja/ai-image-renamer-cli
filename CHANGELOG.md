# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1

### v1.2.0

#### Added

* **Retry Logic:** API calls now retry up to 3 times with exponential backoff for transient failures
* **Timeout:** Added 30-second request timeout to prevent hanging on stalled connections
* **Batch Summary:** Processing now prints a summary of results (renamed, skipped, failed counts)
* **Grammar Fix:** Singular/plural "word" correction in API prompt

#### Changed

* **Image Limit:** CLI now caps processing at 3 images per invocation (down from unlimited)
* **Output Destinations:** Progress messages now go to stderr; only the summary goes to stdout
* **Message Construction:** Replaced fragile `json.loads(f-string)` with native Python data structures (security improvement)
* **Model Reference:** Updated all docstrings from Llama 4 Maverick to Llama 4 Scout

#### Fixed

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
