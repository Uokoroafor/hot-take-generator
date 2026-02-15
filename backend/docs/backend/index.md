# Backend Overview

The backend is a FastAPI application that receives hot-take requests, orchestrates AI agents, and enriches responses with optional search context. This page summarises the architecture so you can reason about changes quickly.

## Request Flow

1. **Routes** (`app.api.routes`): `/api/generate` accepts a `HotTakeRequest` and validates payloads via Pydantic (supports `agent_type`, `use_web_search`, `use_news_search`, `max_articles`, and `web_search_provider`). Additional `/api/agents` and `/api/styles` endpoints expose metadata for the frontend. `length` is currently a placeholder and not yet used in prompts.
2. **Service layer** (`app.services.hot_take_service.HotTakeService`): Chooses an AI agent, gathers optional web/news context, and returns both formatted context text plus structured `sources` metadata.
3. **Agents** (`app.agents.*`): Concrete implementations for OpenAI and Anthropic inherit from a shared `BaseAgent`. Each agent:
   - fetches unified prompts from `PromptManager`
   - assembles a chat completion/message payload
   - returns generated text on success
   - raises runtime errors on provider/API failure
4. **Search Providers** (`app.services.search_providers.*`): Async providers for Brave and Serper implement a common interface to normalize results, which are then turned into LLM-ready context and `SourceRecord` objects.
5. **Schemas** (`app.models.schemas`): Define the request/response contracts for FastAPI and document generator.

## API Contract (Current)

### `POST /api/generate` request

```json
{
  "topic": "artificial intelligence",
  "style": "controversial",
  "length": "medium",
  "agent_type": "openai",
  "use_web_search": true,
  "use_news_search": true,
  "max_articles": 3,
  "web_search_provider": "brave"
}
```

### `POST /api/generate` response

```json
{
  "hot_take": "AI will automate most routine work before teams are ready.",
  "topic": "artificial intelligence",
  "style": "controversial",
  "agent_used": "OpenAI Agent",
  "web_search_used": true,
  "news_context": "Web search results: ...\n\nRecent news and headlines: ...",
  "sources": [
    {
      "type": "web",
      "title": "AI adoption accelerates in 2026",
      "url": "https://example.com/ai-adoption",
      "snippet": "Companies are integrating AI faster than expected...",
      "source": "example.com",
      "published": "2026-01-10T12:00:00+00:00"
    }
  ]
}
```

### `GET /api/agents` response

Returns rich agent metadata (`id`, `name`, `description`, `model`, `temperature`, `system_prompt`) for frontend selection and display.

### `GET /api/styles` response

Returns the list of available style names from `PromptManager`.

## Key Modules

| Module | Responsibility |
| --- | --- |
| `app/main.py` | Configures FastAPI app, CORS, root/health endpoints, and router mounting |
| `app/core/config.py` | Centralised environment configuration using `pydantic-settings` |
| `app/core/prompts.py` | Style catalog, prompt helpers, and agent metadata |
| `app/services/hot_take_service.py` | Glue layer that picks agents, fetches context, and returns `HotTakeResponse` |
| `app/services/web_search_service.py` | Provider-agnostic web search orchestrator |
| `app/services/news_search_service.py` | Asynchronous NewsAPI wrapper with formatting helpers |
| `app/agents/*.py` | Concrete LLM integrations for OpenAI and Anthropic |

## Extending the Backend

- **Add a style**: Update `StylePrompts.BASE_PROMPTS` and the new option automatically flows through the `/api/styles` endpoint.
- **Add an LLM provider**:
  1. Implement a new agent by subclassing `BaseAgent`.
  2. Instantiate it in `HotTakeService.__init__`.
  3. Provide necessary credentials via `.env`.
- **Add a search provider**:
  1. Implement `SearchProvider` (async `search`, `is_configured`, `name`).
  2. Register it inside `WebSearchService.providers`.
  3. Document the provider name so clients can opt-in via `web_search_provider`.

## Error Handling & Observability

- Web/news context lookups are non-fatal; failures are logged and generation continues without that context.
- Agent/provider failures are raised and translated by the route layer into a safe `500` response (`"Failed to generate hot take. Please try again."`).
- Health checks at `/health` let deployment targets monitor the process.
- Readiness checks at `/ready` verify at least one AI provider key is configured.

## Related Reading

- [Python API Reference](api.md) for mkdocstrings-generated class/function docs.
- Check `backend/tests/` in the repository for concrete usage examples and integration coverage.
