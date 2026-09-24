# Changelog

All notable changes are recorded in [Conventional Commits](https://www.conventionalcommits.org/) form.
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.5.0 (2026-09-24)

### feat

- **config:** store settings in `~/.config/ai-image-renamer-cli/.env` (`$XDG_CONFIG_HOME/ai-image-renamer-cli/.env` when `XDG_CONFIG_HOME` is set)
- **config:** create that file on first run, directory mode `0700` and file mode `0600`, and keep it across pip and pipx reinstalls
- **model:** default the Groq model to `qwen/qwen3.8-27b`, the Groq model that accepts images

### fix

- **cli:** read an exported `GROQ_API_KEY` when the tool is installed with pip or pipx
- **config:** load the user config with `override=False`, so a blank `GROQ_API_KEY=` cannot erase an exported key
- **config:** stop reading `./config.ini` from the working directory

### docs

- **readme:** document the config-file path and that only `qwen/qwen3.8-27b` accepts images on Groq

### chore

- **repo:** add `.env.example` for `~/.config/ai-image-renamer-cli/.env`
- **repo:** remove the in-repo `docs/` site and `.serena/` from the GitLab tree

## 1.4.0

### feat

- **providers:** add `ollama` and `openai` backends beside hosted `groq`
- **ollama:** call a local Ollama server through `OLLAMA_HOST` and `OLLAMA_MODEL`
- **openai:** call any OpenAI-compatible server through `OPENAI_API_BASE`, `OPENAI_API_KEY`, and `OPENAI_MODEL`
- **cli:** add `--provider` with choices `groq`, `ollama`, and `openai`
- **deps:** add the `ai-image-renamer[local]` extra for the `openai` package
- **docs:** add the VitePress site and the GitHub Pages workflow

### refactor

- **utils:** share request building, retries, and description parsing across providers
- **renamer:** forward `provider` to `get_words()`

## 1.3.0

### feat

- **config:** add `config.ini` for the API key, model, temperature, timeout, retries, and word count
- **config:** add `MAX_FILENAME_LENGTH` and `REASONING_EFFORT`
- **cli:** add `--api-key` and `--model`
- **cli:** expand `*`, `?`, and `[` globs in image paths
- **filenames:** enforce the requested word count and truncate on keyword boundaries

### fix

- **api:** send `reasoning_effort=none` so Qwen does not emit thinking text
- **cli:** show which files are processed and which are skipped past the 3-image cap

### refactor

- **prompt:** ask for visible keywords and nothing else
- **config:** read temperature, timeout, and retries from the config file

### docs

- **readme:** document `config.ini`, the new flags, word enforcement, and reasoning suppression

### chore

- **gitignore:** ignore `config.ini` so an API key is not committed

## 1.2.0

### feat

- **api:** retry failed calls up to 3 times with exponential backoff
- **api:** abort a stalled request after 30 seconds
- **cli:** print a summary of renamed, skipped, and failed files
- **readme:** add a table of contents and a Groq limits section

### fix

- **api:** build the chat payload with native objects instead of `json.loads` on an f-string
- **cli:** cap one invocation at 3 images
- **tests:** collect the suite when optional dependencies are not installed

### refactor

- **imports:** load `filetype`, `groq`, and `dotenv` inside the functions that use them
- **cli:** send progress to stderr and the summary to stdout

### docs

- **readme:** reword the guide and comment every command in the examples
- **agents:** translate the project guide to English

## 1.1.0

### feat

- **package:** add `main.py`, `__version__`, and `__all__`

### fix

- **model:** replace deprecated Llama 4 Maverick with Llama 4 Scout
- **imports:** use package-relative imports in `renamer.py`
- **tests:** import the package from an install and from a source checkout

### docs

- **modules:** document the CLI, renamer, and utility functions

## 1.0.0

### feat

- **cli:** initial release of AI Image Renamer
