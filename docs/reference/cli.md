# CLI Reference

The `rename_images` command is the entry point to the tool.

Settings are read from `~/.config/ai-image-renamer-cli/.env`, or from `$XDG_CONFIG_HOME/ai-image-renamer-cli/.env` when `XDG_CONFIG_HOME` is set.

## Synopsis

```
rename_images [options] image_paths...
```

## Arguments

### `image_paths` (positional, required)

One or more paths to image files. Accepts multiple files and glob patterns.

```bash
rename_images photo.jpg
rename_images image1.png image2.jpg image3.webp
rename_images ~/Desktop/*.png
```

Supported formats: JPEG, PNG, WebP, GIF, and any other format detected as an image by magic-byte inspection.

::: warning
The CLI processes at most **3 images** per invocation. Excess images are truncated with a warning.
:::

## Options

### `--words`, `-w <N>`

Number of words in the generated filename.

- Range: `1` – `50`
- Default: `DEFAULT_WORD_COUNT` from the user config file (falls back to `6`)

```bash
rename_images -w 3 cat.jpg   # → orange-cat-sleeping.jpg
```

### `--provider <PROVIDER>`

AI backend to use for this invocation.

- Choices: `groq`, `ollama`, `openai`
- Default: `PROVIDER` from the user config file (falls back to `groq`)

```bash
rename_images --provider ollama photo.jpg
rename_images --provider openai --model my-vision-model photo.jpg
```

### `--api-key <KEY>`

API key for this invocation.

- Overrides the exported `GROQ_API_KEY` environment variable and the user config file
- Applies to the `groq` provider; Ollama uses a built-in dummy key
- Get a free Groq key at https://console.groq.com/keys

```bash
rename_images --api-key gsk_xxx photo.jpg
```

### `--model <MODEL>`

AI model for this invocation.

- Overrides `GROQ_MODEL` env var / `MODEL` config key for Groq
- On Groq, only `qwen/qwen3.8-27b` accepts images
- Overrides `OLLAMA_MODEL` for Ollama and `OPENAI_MODEL` for OpenAI-compatible

```bash
rename_images --model qwen/qwen3.8-27b photo.jpg
rename_images --provider ollama --model minicpm-v photo.jpg
```

### `--version`, `-v`

Display the version and exit.

```bash
rename_images -v
# rename_images 1.5.0
```

### `--help`, `-h`

Show usage information and exit.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success (or version/help shown) |
| `1` | argparse error (invalid arguments) |
| Non-zero | Unhandled exception propagated from the pipeline |

## Output

- **Progress messages** go to stderr: `Processing …`, `Renamed … to …`
- **Final summary** goes to stdout:

```
Done: 2 renamed, 1 skipped, 0 failed (out of 3)
```

## Examples

```bash
# Rename a single image with defaults
rename_images path/to/your/image.jpg

# Rename up to 3 images at once
rename_images image1.png image2.jpg image3.webp

# Control filename length
rename_images -w 5 DSC_1234.jpg

# Rename every PNG in a directory
rename_images ~/Desktop/my-photos/*.png

# Use the local Ollama server
rename_images --provider ollama photo.jpg

# Use a custom OpenAI-compatible endpoint
rename_images --provider openai --model my-model photo.jpg

# Full control: provider, model, word count
rename_images --provider ollama --model llava:latest -w 4 photo.jpg

# Show version
rename_images -v
```

## Run from source

```bash
# Via the dev entry point
python main.py photo.jpg

# Via the module entry point
python -m ai_image_renamer.cli photo.jpg
```
