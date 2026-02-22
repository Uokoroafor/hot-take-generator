# Hot Take Generator Backend

This backend powers the Hot Take Generator experience. A FastAPI service orchestrates AI agents (OpenAI & Anthropic), optional search integrations, and reusable prompts to produce timely opinions with contextual flavor.

## What You Get

- **Production-ready FastAPI app** with strict schemas, CORS, health endpoints, and typed responses.
- **Pluggable agents** managed by `HotTakeService`, letting you add or swap LLM providers.
- **Search integrations** that combine NewsAPI-powered context with configurable web search providers (Brave, Serper).
- **Unified prompt strategy** so the tone of each take stays consistent regardless of agent choice.
- **Comprehensive tests** under `backend/tests` covering routes, services, and provider fallbacks.

## Repository Layout

```
backend/
├── app/                # FastAPI package (agents, services, API routes, models)
├── docs/               # MkDocs content (this site)
├── mkdocs.yml          # Site configuration with Material theme & mkdocstrings
├── pyproject.toml      # Backend dependencies managed with uv
└── tests/              # pytest suite for agents, API, and integrations
```

## Next Steps

- **New to the project?** Start with [Getting Started](getting-started.md) to set up your environment.
- **Configuring `.env` files?** Use [Environment Variables](environment-variables.md) as the single source of truth.
- **Need a mental model?** Visit [Backend Overview](backend/index.md) for architecture diagrams and extension tips.
- **Looking for code-level docs?** See the [Python API Reference](backend/api.md) powered by mkdocstrings.
- **Curious about the UI?** The [Frontend overview](frontend/index.md) summarises the React client and how it communicates with this API.
