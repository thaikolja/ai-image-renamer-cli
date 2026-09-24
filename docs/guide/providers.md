# Providers

AI Image Renamer supports three AI backends, selectable via the `PROVIDER` config key or the `--provider` CLI flag.

| Provider | Config value | Hosted / Local | Requires |
|----------|-------------|----------------|----------|
| [Groq](#groq) | `groq` | Hosted | API key |
| [Ollama](#ollama) | `ollama` | Local | Ollama + vision model |
| [OpenAI-compatible](#openai-compatible-endpoints) | `openai` | Local or hosted | Running endpoint |

## Groq

The default provider. Images are sent to Groq's hosted multimodal API, processed in milliseconds, and never stored.

### Setup

```bash
# 1. Get a free API key at https://console.groq.com/keys

# 2. Configure it in ~/.config/ai-image-renamer-cli/.env
```

```ini
PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
MODEL=qwen/qwen3.8-27b
```

Or via environment variable:

```bash
export GROQ_API_KEY="your-key-here"
```

### Vision model

On Groq, only [`qwen/qwen3.8-27b`](https://console.groq.com/docs/model/qwen/qwen3.8-27b) accepts images. Other Groq models are text-only and cannot describe a picture. Keep `MODEL` set to that id.

### Limits

Groq's hosted API has practical limits:

- Images must be **under 20 MB**
- Resolution should stay **under 33 megapixels** (resize high-res photos first)
- Base64-encoded data must stay **under 4 MB**
- Up to 3 images per request (the CLI sends at most 3)

## Ollama

Run everything **locally** — your images never leave your machine. Ollama exposes an OpenAI-compatible endpoint that the tool talks to via the `openai` Python package.

### Setup

```bash
# 1. Install Ollama: https://ollama.com

# 2. Start the server
ollama serve

# 3. Pull a vision model
ollama pull llava

# 4. Install the CLI with local support
pip install "ai-image-renamer[local]"
```

### Configuration

```ini
PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434/v1
OLLAMA_MODEL=llava:latest
```

Or per invocation:

```bash
rename_images --provider ollama photo.jpg
```

### Recommended vision models

| Model | Pull command | Size | Notes |
|-------|-------------|------|-------|
| `llava` | `ollama pull llava` | ~4.7 GB | Classic, reliable, runs on most machines |
| `minicpm-v` | `ollama pull minicpm-v` | ~5.5 GB | Better accuracy, newer architecture |
| `bakllava` | `ollama pull bakllava` | ~5.5 GB | LLaVA fork with stronger image understanding |
| `gemma3:12b` | `ollama pull gemma3:12b` | ~8 GB | Best quality, requires more VRAM |

::: tip
Check Ollama's [vision model library](https://ollama.com/search?c=vision) for the full list of models with image support.
:::

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `Connection refused` | Start the server: `ollama serve` |
| `model not found` | Pull the model first: `ollama pull <model>` |
| `The 'openai' package is required` | Install the local extra: `pip install "ai-image-renamer[local]"` |
| `Ollama not found` | Install from https://ollama.com |
| Slow responses | Try a smaller model (e.g. `llava` instead of `gemma3:12b`) |

## OpenAI-compatible endpoints

Any server speaking the OpenAI Chat Completions API works — LM Studio, vLLM, llama.cpp, text-generation-webui, and hosted services like OpenRouter or Together.

### Setup

```bash
# 1. Start your server (e.g. LM Studio → Local Server → Start)
#    The default LM Studio endpoint is http://localhost:1234/v1

# 2. Install the CLI with local support
pip install "ai-image-renamer[local]"
```

### Configuration

```ini
PROVIDER=openai
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_MODEL=my-vision-model
OPENAI_API_KEY=local-key   # required only if the server demands one
```

Or per invocation:

```bash
rename_images --provider openai --model my-vision-model photo.jpg
```

### Known good endpoints

| Server | Default base URL |
|--------|------------------|
| LM Studio | `http://localhost:1234/v1` |
| vLLM | `http://localhost:8000/v1` |
| llama.cpp server | `http://localhost:8080/v1` |
| Ollama (legacy) | `http://localhost:11434/v1` |

## Model override

Any provider's model can be overridden at runtime:

```bash
# Groq model override
rename_images --model qwen/qwen3.8-27b photo.jpg

# Ollama model override
rename_images --provider ollama --model minicpm-v photo.jpg
```

## Provider comparison

| | Groq | Ollama | OpenAI-compatible |
|---|------|--------|-------------------|
| Privacy | Images sent to Groq | Fully local | Depends on server |
| Speed | Milliseconds | Depends on hardware | Depends on hardware |
| Cost | Free tier available | Free | Usually free |
| Setup effort | API key only | Install Ollama + pull model | Run a server |
| Best for | Quick cloud usage | Privacy, offline, no accounts | Custom or existing infrastructure |
