# Search Services

This page documents how search context is gathered and normalized before prompt generation.

## Overview

Search is split into two services:

- `NewsSearchService`: fetches recent articles (NewsAPI)
- `WebSearchService`: fetches general web results through pluggable providers

Both can be enabled together and their context is combined for generation.

## Architecture

```text
app/services/
├── news_search_service.py
├── web_search_service.py
└── search_providers/
    ├── base.py
    ├── brave_provider.py
    └── serper_provider.py
```

## Request Usage

`POST /api/generate` supports:

- `use_web_search` (`true`/`false`)
- `use_news_search` (`true`/`false`)
- `max_articles` (limit results)
- `web_search_provider` (`brave`, `serper`, or omitted for auto-select)

Example:

```json
{
  "topic": "artificial intelligence",
  "style": "controversial",
  "use_web_search": true,
  "use_news_search": true,
  "max_articles": 3,
  "web_search_provider": "brave"
}
```

## Environment Variables

- `NEWSAPI_API_KEY` enables news context
- `BRAVE_API_KEY` enables Brave provider
- `SERPER_API_KEY` enables Serper provider

If no provider is configured, generation continues without search context.

## Provider Behavior

- `WebSearchService` normalizes different provider response formats.
- If `web_search_provider` is omitted, the first configured provider is used.
- Search failures are non-fatal; hot take generation still proceeds.

## Extending Providers

1. Implement `SearchProvider` in `app/services/search_providers/`.
2. Register it in `WebSearchService.providers`.
3. Add provider credentials to `app/core/config.py`.
4. Document the provider name for API clients.

## Testing

```bash
cd backend
uv run pytest tests/test_search_providers.py
uv run pytest tests/test_news_search.py
uv run pytest tests/test_web_search.py
```

For full backend flow context, see `architecture.md`.
