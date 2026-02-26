# Hot Take Generator

[![CI Pipeline](https://github.com/Uokoroafor/hot-take-generator/actions/workflows/main.yaml/badge.svg)](https://github.com/Uokoroafor/hot-take-generator/actions)
[![Coverage](https://raw.githubusercontent.com/Uokoroafor/hot-take-generator/badges/backend/coverage.svg)](https://github.com/Uokoroafor/hot-take-generator/tree/badges/backend)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A full-stack app that generates spicy, controversial opinions on any topic using AI agents powered by OpenAI and Anthropic models.

> **Note:** This is a fun personal project. Model outputs can be inaccurate, biased, or hilariously wrong. That's kind of the point.

## About

Inspired by [The Arsenal Opinion Podcast](https://www.le-grove.co.uk/s/the-arsenal-opinion-podcast), which kicks off each episode with a "Hottest of Takes" segment -- bold, controversial opinions about anything Arsenal FC. I wanted to capture that same energy with AI: a tool that can instantly craft witty, controversial, or thought-provoking takes on any topic.

## Features

- **Multiple AI Agents** -- Choose between OpenAI (GPT) and Anthropic (Claude)
- **9 Styles** -- Controversial, sarcastic, optimistic, pessimistic, absurd, analytical, philosophical, witty, contrarian
- **Web Search** -- Optionally pull in recent news for timely takes
- **Dark Mode** -- Because of course
- **Share** -- Copy or tweet your favourite takes

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Backend** | FastAPI, Python 3.11+, Pydantic v2, HTTPX |
| **Frontend** | React 19, TypeScript, Vite |
| **AI** | OpenAI API, Anthropic API |
| **Infra** | Render (backend), Vercel (frontend), GitHub Actions CI |

## Quick Start

### Prerequisites

- Python 3.11+ and [UV](https://docs.astral.sh/uv/)
- Node.js 22+
- API keys for [OpenAI](https://platform.openai.com/) and/or [Anthropic](https://console.anthropic.com/)

### Setup

```bash
git clone https://github.com/Uokoroafor/hot-take-generator.git
cd hot-take-generator

# Install deps and start both servers
make quick-start
```

Add your API keys to `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Then visit **http://localhost:5173**. API docs are at **http://localhost:8000/docs**.

> For Docker setup and manual installation, see [DEVELOPERS.md](./DEVELOPERS.md).
> For all environment variables (backend + frontend), see [Environment Variables](./backend/docs/environment-variables.md).

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate` | Generate a hot take |
| `GET` | `/api/styles` | List available styles |
| `GET` | `/api/agents` | List available AI agents |
| `GET` | `/health` | Health check |

<details>
<summary>Example request</summary>

```json
{
  "topic": "pineapple on pizza",
  "style": "controversial",
  "use_web_search": false
}
```

</details>

## Caching

The backend supports optional Redis caching for no-search generation requests:

- If `use_web_search=false` and `use_news_search=false`, the service stores generated responses in a per-topic/style variant pool.
- The pool grows up to `CACHE_VARIANT_POOL_SIZE` (default `5`).
- While the pool has fewer than 5 variants, requests still call the LLM and append new variants.
- Once the pool is full, requests return a random cached variant instead of calling the LLM.
- If Redis is unavailable, the app gracefully falls back to direct LLM generation.

## Development

```bash
make dev             # Start both servers
make test            # Run all tests
make lint            # Lint everything
make help            # See all commands
```

For detailed setup, testing, troubleshooting, and contribution guides, see [DEVELOPERS.md](./DEVELOPERS.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution workflow and [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) for community guidelines.

## Roadmap

See [TODO.md](./TODO.md) for the full roadmap. Highlights:

- Adjustable take hotness ("spice level") controls in the UI (not raw LLM sampling temperature)
- Style Presets integration
- Text-to-speech playback

## License

MIT License -- see [LICENSE](./LICENSE) for details.
