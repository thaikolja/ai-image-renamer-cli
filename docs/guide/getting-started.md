# Getting Started

This guide walks you through your first rename — from installation to a working command.

## 1. Install the tool

Pick one installation method from the [Installation guide](/guide/installation). The quickest is:

```bash
pip install ai-image-renamer
```

If you plan to use local LLMs, install with the local extra:

```bash
pip install "ai-image-renamer[local]"
```

## 2. Choose a provider

The tool works with three AI backends:

| Provider | Description | Requires |
|----------|-------------|----------|
| `groq` (default) | Hosted Groq API — fast, free tier available | A Groq API key |
| `ollama` | Your local Ollama server — fully private | Ollama installed + a vision model pulled |
| `openai` | Any OpenAI-compatible endpoint (LM Studio, vLLM, llama.cpp, …) | A running server + endpoint URL |

See the [Providers guide](/guide/providers) for full setup instructions for each.

## 3. Configure

On first run, a commented `.env` file is auto-generated at `~/.config/ai-image-renamer-cli/.env`. Open it and set at minimum the API key for your provider:

```ini
PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
```

Alternatively, export the key. It overrides the config file. The `export` is required; a bare assignment in `.zshrc` is visible to `echo` and is not inherited by the program:

```bash
export GROQ_API_KEY="your-key-here"
```

Everything else — model, temperature, word count, timeouts — has sensible defaults. See [Configuration](/guide/configuration) for the full list.

## 4. Rename your first image

```bash
rename_images path/to/your/image.jpg
```

Expected output:

```
Processing path/to/your/image.jpg...
Renamed path/to/your/image.jpg to /path/to/sunset-beach-palm-trees.jpg
Done: 1 renamed, 0 skipped, 0 failed (out of 1)
```

Your image now has a descriptive, searchable filename.

## 5. Try the variations

```bash
# Rename multiple images (max 3 per invocation)
rename_images image1.png image2.jpg image3.webp

# Control the filename length (1-50 words)
rename_images -w 3 DSC_123.jpg

# Use glob patterns
rename_images ~/Desktop/*.png

# Switch provider for a single invocation
rename_images --provider ollama photo.jpg

# Override the model
rename_images --model llava:latest --provider ollama photo.jpg
```

## Next steps

- Explore all [CLI options](/reference/cli)
- Learn about every [config key](/reference/config-keys)
- Set up a [local provider](/guide/providers) for offline renaming
