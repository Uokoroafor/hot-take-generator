# Search Services Guide

This guide explains the new architecture for web search and news search in the Hot Take Generator.

## Overview

The search functionality has been refactored to separate **web search** from **news search**, with support for multiple search providers.

### Architecture

```
app/services/
├── search_providers/           # Search provider implementations
│   ├── __init__.py
│   ├── base.py                # Abstract base class
│   ├── brave_provider.py      # Brave Search API
│   └── serper_provider.py     # Serper/Google Search API
├── web_search_service.py      # General web search service
└── news_search_service.py     # News-specific search service
```

## Services

### 1. NewsSearchService

**Purpose**: Search for recent news articles using NewsAPI.

**Usage**:
```python
from app.services.news_search_service import NewsSearchService

service = NewsSearchService()
articles = await service.search_recent_news("artificial intelligence", max_results=5)
formatted_context = service.format_news_context(articles)
```

**API Key Required**: `NEWSAPI_API_KEY` in `.env`

### 2. WebSearchService

**Purpose**: General web search with pluggable providers (Brave, Serper).

**Features**:
- Auto-selects first configured provider if none specified
- Supports multiple providers with consistent interface
- Easy to add new providers

**Usage**:
```python
from app.services.web_search_service import WebSearchService

# Auto-select provider (uses first configured)
service = WebSearchService()

# Or specify a provider
service = WebSearchService(provider_name="brave")

# Search
results = await service.search("climate change", max_results=5)
formatted_context = service.format_search_context(results)
```

**API Keys** (in `.env`):
- `BRAVE_API_KEY` - For Brave Search (free tier available)
- `SERPER_API_KEY` - For Serper/Google Search

## Search Providers

### Brave Search Provider

**Provider**: `brave`
**Website**: https://brave.com/search/api/
**Free Tier**: Yes (limited requests)

**Features**:
- Fast general web search
- Good coverage
- Privacy-focused

### Serper Provider

**Provider**: `serper`
**Website**: https://serper.dev/
**Free Tier**: Yes (limited requests)

**Features**:
- Google search results
- High quality results
- Good for specific queries

## Configuration

Add API keys to your `.env` file:

```bash
# News search
NEWSAPI_API_KEY=your_newsapi_key_here

# Web search (choose one or both)
BRAVE_API_KEY=your_brave_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## API Usage

### Request Parameters

```json
{
  "topic": "artificial intelligence",
  "style": "controversial",
  "use_web_search": true,
  "use_news_search": true,
  "max_articles": 3,
  "web_search_provider": "brave"  // Optional: "brave", "serper", or null for auto
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "climate change",
    "style": "controversial",
    "use_web_search": true,
    "use_news_search": true,
    "max_articles": 5,
    "web_search_provider": "brave"
  }'
```

## HotTakeService Integration

The `HotTakeService` now supports both web and news search:

```python
result = await hot_take_service.generate_hot_take(
    topic="AI ethics",
    style="controversial",
    use_web_search=True,        # General web search
    use_news_search=True,       # News articles
    max_articles=3,
    web_search_provider="brave" # Optional
)
```

**Context Combination**:
- If both `use_web_search` and `use_news_search` are enabled, contexts are combined
- The LLM receives both web search results and news articles
- Provides more comprehensive context for hot take generation

## Adding a New Search Provider

1. Create a new provider class in `app/services/search_providers/`:

```python
from .base import SearchProvider

class NewProvider(SearchProvider):
    async def search(self, query: str, max_results: int = 5):
        # Implementation
        pass

    def is_configured(self) -> bool:
        return bool(settings.new_provider_api_key)

    @property
    def name(self) -> str:
        return "new_provider"
```

2. Add the API key to `app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings
    new_provider_api_key: Optional[str] = None
```

3. Register the provider in `WebSearchService`:

```python
self.providers = {
    "brave": BraveSearchProvider(),
    "serper": SerperSearchProvider(),
    "new_provider": NewProvider(),  # Add here
}
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_search_providers.py
pytest tests/test_news_search.py
pytest tests/test_web_search.py
```

### External Integration Tests

Tests marked with `@pytest.mark.external` require actual API keys:

```bash
# Run external tests (requires API keys)
pytest tests/ -m external
```

## Differences from Old System

### Before
- Single `WebSearchService` that only used NewsAPI
- No separation between news and general web search
- No support for multiple providers

### After
- `NewsSearchService` for news-specific searches (NewsAPI)
- `WebSearchService` for general web searches (Brave, Serper, etc.)
- Pluggable provider architecture
- Can use both services simultaneously
- Easy to add new search providers

## Benefits

1. **Separation of Concerns**: News and web search are now separate services
2. **Flexibility**: Choose your preferred search provider
3. **Free Options**: Brave Search offers a free tier
4. **Extensibility**: Easy to add new providers
5. **Better Context**: Combine news and web results for richer context

## Troubleshooting

### No search results
- Verify API keys are correctly set in `.env`
- Check API key validity and rate limits
- Ensure network connectivity

### Provider not found
- Check provider name spelling (`"brave"` or `"serper"`)
- Verify provider is registered in `WebSearchService`

### Import errors
- Ensure all new files are created
- Check `__init__.py` files exist in new directories

## Next Steps

To use the new search services:

1. Choose your preferred web search provider (Brave or Serper)
2. Sign up for an API key
3. Add the API key to your `.env` file
4. Update your requests to use `use_web_search` and/or `use_news_search`
5. Optionally specify `web_search_provider` to choose a specific provider
