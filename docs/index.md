---
layout: home

hero:
  name: AI Image Renamer
  text: Descriptive filenames, automatically
  tagline: A command-line tool that uses AI to analyze your images and rename them with clean, searchable, SEO-friendly filenames.
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: Installation
      link: /guide/installation
    - theme: alt
      text: View on GitHub
      link: https://github.com/thaikolja/ai-image-renamer

features:
  - icon: 🤖
    title: AI-powered
    details: Uses state-of-the-art vision language models to describe what's visible in your images.
  - icon: ⚡️
    title: Blazing fast
    details: Groq's hosted infrastructure processes files in milliseconds — or run locally with Ollama for full privacy.
  - icon: 🔎
    title: SEO-friendly names
    details: Generated filenames are lowercase, hyphen-separated, and optimized for search and organization.
  - icon: 🏠
    title: Local-first option
    details: Bring your own local LLM with Ollama, LM Studio, vLLM, or any OpenAI-compatible endpoint.
  - icon: 📚
    title: Batch processing
    details: Rename up to 3 images per invocation with automatic overwrite protection.
  - icon: 🛡️
    title: Safe by design
    details: Magic-byte validation, filename sanitization, and retry logic with exponential backoff.
---

## What is AI Image Renamer?

**AI Image Renamer** is a Python CLI tool that turns `IMG_4821.jpg` into `sunset-beach-palm-trees.jpg` by asking an AI vision model what's in the picture.

It's perfect for:

- **Organizing photo collections** — replace camera-generated filenames with descriptive ones
- **Preparing web assets** — generate SEO-friendly filenames before uploading
- **Learning AI integration** — a clean, well-tested example of multimodal AI usage in Python

## How it works

```
image file → magic-byte validation → base64 encoding → AI vision model
    → description ("sunset beach palm trees") → sanitization → rename
```

The AI model receives your image and returns a short keyword description, which is then converted into a clean filename: lowercase, non-alphabetic characters stripped, spaces converted to hyphens, and truncated at keyword boundaries.

## Quick start

```bash
pip install ai-image-renamer
rename_images photo.jpg
```

That's it. The first run auto-generates a commented config file at `~/.config/ai-image-renamer-cli/.env` — just add your API key (or configure a local provider) and go.

::: tip
Prefer full privacy? Point the tool at a local [Ollama](/guide/providers#ollama) server and keep your images on your machine.
:::
