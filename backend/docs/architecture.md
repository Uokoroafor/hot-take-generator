# Backend Architecture

This document describes how a user request flows through the backend to generate a hot take.

## Request Flow Overview

```
┌─────────────┐
│   Client    │
│  (React)    │
└──────┬──────┘
       │ POST /api/generate
       ▼
┌─────────────┐
│   Routes    │
│ (FastAPI)   │
└──────┬──────┘
       │ HotTakeRequest
       ▼
┌─────────────┐
│ HotTake     │
│ Service     │
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌─────┐  ┌─────────┐
│Agent│  │ Search  │
│     │  │Services │
└──┬──┘  └────┬────┘
   │          │
   │   ┌──────┴──────┐
   │   ▼             ▼
   │ ┌─────┐    ┌─────────┐
   │ │News │    │   Web   │
   │ │ API │    │ Search  │
   │ └─────┘    └─────────┘
   │
   ▼
┌─────────────┐
│  LLM API    │
│(OpenAI/     │
│ Anthropic)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Client    │
│  (React)    │
└─────────────┘
```

## Detailed Flow

### 1. API Route (`app/api/routes.py`)

The client sends a POST request to `/api/generate`:

```json
{
  "topic": "remote work",
  "style": "controversial",
  "agent_type": "openai",
  "use_web_search": true,
  "use_news_search": true,
  "max_articles": 3,
  "web_search_provider": "brave"
}
```

**Request Fields:**
- `topic` (required) - The subject for the hot take
- `style` (optional) - One of: controversial, sarcastic, optimistic, pessimistic, absurd, analytical, philosophical, witty, contrarian
- `agent_type` (optional) - Specific agent to use: `"openai"`, `"anthropic"`, or `null` for random selection
- `use_web_search` (optional) - Include general web search results
- `use_news_search` (optional) - Include recent news articles
- `max_articles` (optional) - Number of articles to fetch (default 3; provider-specific limits apply)
- `web_search_provider` (optional) - Specific search provider: `"brave"`, `"serper"`, or `null` for auto-selection

The route validates the request using Pydantic schemas and delegates to `HotTakeService`. Agent metadata is exposed via `/api/agents`.

### 2. Hot Take Service (`app/services/hot_take_service.py`)

The orchestration layer that:

1. **Selects an agent** - Uses requested `agent_type` (openai/anthropic) or randomly selects one if not specified
2. **Checks cache for no-search requests**:
   - Cache key shape: `hot_take:{topic}:{style}[:agent_type]`
   - Uses a variant pool (`CACHE_VARIANT_POOL_SIZE`, default 5)
   - If pool is full, returns a random cached variant
   - If pool is not full, continues to generate a fresh result and appends it to the pool
3. **Gathers context** (if `use_web_search` or `use_news_search` is true):
   - Fetches recent news via `NewsSearchService`
   - Fetches web results via `WebSearchService`
   - Builds structured `SourceRecord[]` for tracking
4. **Builds the prompt** - Combines topic, style, and context
5. **Calls the agent** - Sends prompt to the LLM (raises exceptions on failure)
6. **Returns response** - Wraps result in `HotTakeResponse` with structured sources

### 3. Search Services

#### News Search Service (`app/services/news_search_service.py`)

- Queries NewsAPI for recent articles on the topic
- Extracts headlines, descriptions, sources, and publish dates
- Returns structured article data (not just formatted strings)
- Formats as context string for the LLM

#### Web Search Service (`app/services/web_search_service.py`)

- Queries configured provider (Brave or Serper via SearchProvider interface)
- Returns top search results with titles, snippets, URLs
- Normalizes results across providers into consistent format
- Auto-selects first configured provider if none specified

#### Source Tracking

The service builds structured `SourceRecord` objects from search results:

```python
class SourceRecord(BaseModel):
    type: Literal["web", "news"]
    title: str
    url: str
    snippet: Optional[str] = None
    source: Optional[str] = None
    published: Optional[datetime] = None
```

**Helper Methods:**
- `_build_web_source_records(results)` - Transforms web search results to SourceRecord[]
- `_build_news_source_records(articles)` - Transforms news articles to SourceRecord[]

These structured sources enable:
- Frontend source tracking and display in SourcesPage
- Deduplication across generations
- Attribution and citation
- Historical source browsing

### 4. Agents (`app/agents/`)

Each agent implements `BaseAgent` with a `generate()` method:

#### OpenAI Agent (`app/agents/openai_agent.py`)
- Uses OpenAI Chat Completions API
- Supports GPT-4 and GPT-3.5 models

#### Anthropic Agent (`app/agents/anthropic_agent.py`)
- Uses Anthropic Messages API
- Supports Claude models

Both agents:
1. Get system prompt from `PromptManager` based on style and context type
2. Build messages array with system prompt and user topic
3. Call the LLM API (OpenAI Chat Completions or Anthropic Messages)
4. Return generated text on success
5. **Raise `RuntimeError` on failure** (not error strings) for proper HTTP error handling

### 5. Prompt Management (`app/core/prompts.py`)

Centralised prompt templates for each style:

- **Controversial** - Bold, provocative opinions
- **Sarcastic** - Sharp wit with humour
- **Analytical** - Deep, nuanced breakdowns
- etc.

The `PromptManager` class provides:
- `get_full_prompt(agent_type, style, with_news)` - Returns complete system prompt for given agent, style, and context type
- `get_all_available_styles()` - Lists all available styles

### 6. Cache Service (`app/services/cache.py`)

- Uses Redis when `REDIS_URL` is configured.
- Stores cached responses as a JSON array (variant pool) per key.
- Applies TTL via `CACHE_TTL_SECONDS`.
- Gracefully disables caching if Redis is not configured or unavailable.

### 7. Langfuse Tracing for Cache Behavior

Generation observations include cache metadata for no-search requests:

- `cache_hit` - `true` when serving from a full cache pool, otherwise `false`
- `cache_pool_size` - number of variants currently available for that key

This makes cache effectiveness visible in Langfuse without changing API responses.

## Response Flow

The response travels back through the same layers:

```json
{
  "hot_take": "Remote work is just corporate-sponsored agoraphobia...",
  "topic": "remote work",
  "style": "controversial",
  "agent_used": "OpenAI Agent",
  "web_search_used": true,
  "news_context": "Recent articles: ...",
  "sources": [
    {
      "type": "web",
      "title": "The Future of Remote Work",
      "url": "https://example.com/article",
      "snippet": "Companies are rethinking their office strategies...",
      "source": "TechCrunch",
      "published": "2024-01-15T10:30:00Z"
    },
    {
      "type": "news",
      "title": "Remote Work Trends 2024",
      "url": "https://news.example.com/remote-work",
      "snippet": "Latest statistics show...",
      "source": "Business News",
      "published": "2024-01-16T14:20:00Z"
    }
  ]
}
```

**Response Fields:**
- `hot_take` - The generated opinion text
- `topic` - Echo of the input topic
- `style` - Echo of the style used
- `agent_used` - Name of the agent that generated the take (e.g., "OpenAI Agent", "Claude Agent")
- `web_search_used` - Boolean indicating if any search context was used
- `news_context` - Combined formatted text of all search results (for display in UI)
- `sources` - Structured array of `SourceRecord` objects for tracking and display

## API Endpoints

### Core Endpoints

#### `POST /api/generate`
Generates a hot take based on the provided topic and parameters.
- **Request**: `HotTakeRequest` (see Request Flow section above)
- **Response**: `HotTakeResponse` with hot take text and metadata
- **Status Codes**: 200 (success), 422 (validation error), 500 (generation error)

#### `GET /api/agents`
Returns metadata about available AI agents.
- **Response**:
```json
{
  "agents": [
    {
      "id": "openai",
      "name": "OpenAI Agent",
      "description": "Generates hot takes with OpenAI models.",
      "model": "gpt-3.5-turbo",
      "temperature": 0.8,
      "system_prompt": "..."
    },
    {
      "id": "anthropic",
      "name": "Claude Agent",
      "description": "Generates hot takes with Anthropic Claude models.",
      "model": "claude-haiku-4-5-20251001",
      "temperature": 0.8,
      "system_prompt": "..."
    }
  ]
}
```

#### `GET /api/styles`
Returns list of available hot take styles.
- **Response**:
```json
{
  "styles": [
    "controversial",
    "sarcastic",
    "optimistic",
    "pessimistic",
    "absurd",
    "analytical",
    "philosophical",
    "witty",
    "contrarian"
  ]
}
```

### Health Endpoints

#### `GET /health`
Basic health check - always returns 200 if service is running.
- **Response**: `{"status": "healthy"}`

#### `GET /ready`
Readiness probe - checks if service is properly configured.
- **Response**: `{"status": "ready"}` (200) if at least one AI provider API key is configured
- **Response**: `{"status": "not_ready", "missing_configuration": [...]}` (503) if no AI providers configured

## Error Handling

The application follows proper error handling practices:

### Agent Failures
- **LLM API errors** - Agents raise `RuntimeError` (not error strings)
- **Route handler** - Catches exceptions, logs full stack trace with `logger.exception()`
- **HTTP response** - Returns `500 Internal Server Error` with user-safe message
- **Client receives** - Generic error: "Failed to generate hot take. Please try again."
- **Security** - Internal error details never exposed to clients (logged server-side only)

### Validation Errors
- **Invalid input** - Pydantic validation returns `422 Unprocessable Entity` with field-specific details
- **Invalid agent_type** - Validation error if not `"openai"`, `"anthropic"`, or `null`
- **Invalid web_search_provider** - Validation error if not `"brave"`, `"serper"`, or `null`

### Search Service Failures
- **Non-fatal** - Web/news search failures logged as warnings
- **Graceful degradation** - Hot take generation continues without search context
- **No user impact** - Search unavailability doesn't break the core feature

### Missing API Keys
- **Startup check** - `/ready` endpoint returns `503 Service Unavailable` if no AI provider configured
- **Runtime** - At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be set

## Configuration (`app/core/config.py`)

Environment-based settings using `pydantic-settings`:

```python
class Settings(BaseSettings):
    # AI Provider API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Search API Keys
    brave_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    newsapi_api_key: Optional[str] = None

    # Environment Settings
    environment: str = "development"
    debug: bool = True

    # CORS Configuration
    cors_origins: str = "http://localhost:5173"

    def get_cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return origins or ["http://localhost:5173"]
```

**CORS Configuration:**
- `CORS_ORIGINS` environment variable accepts comma-separated origins
- Default: `http://localhost:5173` (local development)
- Production example: `CORS_ORIGINS=https://app.example.com,https://staging.example.com`
- Applied in `main.py` via `CORSMiddleware`

## Adding New Components

### New Style
Add to `StylePrompts.BASE_PROMPTS` in `app/core/prompts.py`

### New Agent
1. Subclass `BaseAgent` in `app/agents/`
2. Implement `generate_hot_take(topic, style, news_context)` method
3. Register in `HotTakeService.__init__`

### New Search Provider
1. Implement `SearchProvider` interface
2. Add to `WebSearchService.providers` list

## Docker Build Architecture

The backend uses a multi-stage Docker build for optimal image size and security:

### Builder Stage
- Base: `python:3.14-slim`
- Installs build dependencies (`build-essential`)
- Installs uv package manager
- Runs `uv sync --frozen` to create virtual environment
- Build artifacts: `/app/.venv` and `/root/.local/share/uv`

### Runtime Stage
- Base: `python:3.14-slim` (fresh image)
- Installs only runtime dependencies (curl, uv)
- Copies virtual environment from builder stage
- Copies uv-managed Python interpreter
- Runs as non-root user `app`
- Final image excludes build tools (gcc, make, etc.)

### Benefits
- **Smaller image size** - Build dependencies not included in final image
- **Better security** - Minimal attack surface, runs as non-root
- **Faster deployments** - Smaller images pull and start faster
- **Layer caching** - Dependencies cached separately from app code

### Volume Exclusions

In development (docker-compose), these directories are excluded from volume mounts to preserve the built artifacts:
- `/app/.venv` - Virtual environment from image
- `/app/.uv` - UV cache directory
