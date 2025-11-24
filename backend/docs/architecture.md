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
  "length": "medium",
  "use_web_search": true,
  "use_news_search": true,
  "max_articles": 3,
  "web_search_provider": "brave"
}
```

The route validates the request using Pydantic schemas and delegates to `HotTakeService`. Agent selection is automatic between the available providers (exposed via `/api/agents`).

> Note: `length` is currently a placeholder; prompts do not yet vary by length.

### 2. Hot Take Service (`app/services/hot_take_service.py`)

The orchestration layer that:

1. **Selects an agent** - Picks the requested agent (OpenAI/Anthropic) or falls back to an available one
2. **Gathers context** (if `use_web_search` is true):
   - Fetches recent news via `NewsSearchService`
   - Fetches web results via `WebSearchService`
3. **Builds the prompt** - Combines topic, style, and context
4. **Calls the agent** - Sends prompt to the LLM
5. **Returns response** - Wraps result in `HotTakeResponse`

### 3. Search Services

#### News Search Service (`app/services/news_search_service.py`)

- Queries NewsAPI for recent articles on the topic (no RSS ingestion)
- Extracts headlines, descriptions, and sources
- Formats as context string for the LLM

#### Web Search Service (`app/services/web_search_service.py`)

- Queries configured provider (Brave or Serper)
- Returns top search results with titles and snippets
- Normalises results across providers

### 4. Agents (`app/agents/`)

Each agent implements `BaseAgent` with a `generate()` method:

#### OpenAI Agent (`app/agents/openai_agent.py`)
- Uses OpenAI Chat Completions API
- Supports GPT-4 and GPT-3.5 models

#### Anthropic Agent (`app/agents/anthropic_agent.py`)
- Uses Anthropic Messages API
- Supports Claude models

Both agents:
1. Get system prompt from `PromptManager` based on style
2. Build messages array with system prompt and user topic
3. Call the LLM API
4. Return generated text

### 5. Prompt Management (`app/core/prompts.py`)

Centralised prompt templates for each style:

- **Controversial** - Bold, provocative opinions
- **Sarcastic** - Sharp wit with humour
- **Analytical** - Deep, nuanced breakdowns
- etc.

The `PromptManager` class provides:
- `get_system_prompt(style)` - Returns style-specific instructions
- `get_available_styles()` - Lists all styles
- `get_agent_metadata()` - Returns agent info for the frontend

## Response Flow

The response travels back through the same layers:

```python
HotTakeResponse(
    hot_take="Remote work is just corporate-sponsored agoraphobia...",
    topic="remote work",
    style="controversial",
    agent_used="openai",
    web_search_used=True,
    news_context="Recent articles: ..."
)
```

## Error Handling

- **Missing API keys** - Service logs warning, returns degraded response
- **API failures** - Caught and logged, fallback to other agent if available
- **Invalid input** - Pydantic validation returns 422 with details
- **Unexpected errors** - Bubble up as 500 HTTPException

## Configuration (`app/core/config.py`)

Environment-based settings using `pydantic-settings`:

```python
class Settings(BaseSettings):
    openai_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    brave_api_key: Optional[str]
    serper_api_key: Optional[str]
    newsapi_api_key: Optional[str]
    environment: str = "development"
    debug: bool = True
```

## Adding New Components

### New Style
Add to `StylePrompts.BASE_PROMPTS` in `app/core/prompts.py`

### New Agent
1. Subclass `BaseAgent` in `app/agents/`
2. Implement `generate(topic, style, context)` method
3. Register in `HotTakeService.__init__`

### New Search Provider
1. Implement `SearchProvider` interface
2. Add to `WebSearchService.providers` list
