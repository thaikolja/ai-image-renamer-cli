# Config Keys Reference

Every key understood by `config.ini`, with defaults and purposes.

| Key | Default | Purpose |
|-----|---------|---------|
| `PROVIDER` | `groq` | AI backend: `groq`, `ollama`, or `openai` |
| `GROQ_API_KEY` | *(empty)* | Groq API key (required for the `groq` provider) |
| `MODEL` | `qwen/qwen3.6-27b` | Groq vision model |
| `OLLAMA_HOST` | `http://localhost:11434/v1` | Ollama OpenAI-compatible endpoint |
| `OLLAMA_MODEL` | `llava:latest` | Ollama vision model |
| `OPENAI_API_BASE` | *(empty)* | OpenAI-compatible endpoint (required for the `openai` provider) |
| `OPENAI_API_KEY` | *(empty)* | API key for the `openai` provider (if required) |
| `OPENAI_MODEL` | *(empty)* | Model name for the `openai` provider (required) |
| `TEMPERATURE` | `1.0` | Output randomness (0.0 – 2.0) |
| `TIMEOUT` | `30` | API request timeout in seconds |
| `MAX_RETRIES` | `3` | Retry attempts on API failure |
| `DEFAULT_WORD_COUNT` | `6` | Default filename word count (1 – 50) |
| `MAX_FILENAME_LENGTH` | `100` | Max filename stem length in characters |
| `REASONING_EFFORT` | `none` | Reasoning suppression for Qwen/GPT-OSS models |

## Provider-specific key resolution

Which config key is used depends on the active provider:

| Setting | `groq` | `ollama` | `openai` |
|---------|--------|----------|----------|
| Endpoint | (built-in) | `OLLAMA_HOST` | `OPENAI_API_BASE` |
| Model | `MODEL` | `OLLAMA_MODEL` | `OPENAI_MODEL` |
| API key | `GROQ_API_KEY` | dummy `ollama` | `OPENAI_API_KEY` (falls back to `local`) |

## Environment variable fallbacks

| Env var | Config key it overrides |
|---------|------------------------|
| `GROQ_API_KEY` | `GROQ_API_KEY` |
| `GROQ_MODEL` | `MODEL` |
| `OPENAI_API_KEY` | `OPENAI_API_KEY` |

## Override order

```
CLI flag  >  environment variable  >  config.ini  >  hardcoded default
```

## Invalid values

Values that fail to parse are handled gracefully:

- Invalid `TEMPERATURE` → warned, falls back to `1.0`
- Invalid `TIMEOUT` → warned, falls back to `30`
- Invalid `MAX_RETRIES` → warned, falls back to `3`
- Invalid `DEFAULT_WORD_COUNT` → warned, falls back to `6`
- Invalid `MAX_FILENAME_LENGTH` → falls back to `100`
