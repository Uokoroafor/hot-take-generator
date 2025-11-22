# Getting Started

Follow this guide to spin up the backend locally, run the API, and execute the automated test suite. All commands assume you are inside the repository root unless stated otherwise.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management (`pip install uv` if needed)
- Make (optional but recommended for the provided recipes)
- Docker + Docker Compose (optional, for containerised workflows)

## Local Development (uv)

```bash
cd backend
uv venv                       # create a virtual environment (uses .venv/)
uv sync                       # install dependencies defined in pyproject.toml
cp .env.example .env          # add your API keys (OpenAI, Anthropic, search providers)
source .venv/bin/activate     # activate the environment on macOS/Linux
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Key environment variables supported by `app.core.config.Settings`:

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Enables the `OpenAIAgent` |
| `ANTHROPIC_API_KEY` | Enables the `AnthropicAgent` |
| `BRAVE_API_KEY` | Turns on Brave search provider |
| `SERPER_API_KEY` | Turns on Serper.dev provider |
| `NEWSAPI_API_KEY` | Enables news context gathering |
| `ENVIRONMENT` | Set to `development` or `production` (default: `development`) |
| `DEBUG` | Enable debug mode (default: `true`) |

The FastAPI docs are available at `http://localhost:8000/docs` once the server is running.

## Makefile Shortcuts

From the repo root:

```bash
make quick-start      # installs backend + frontend deps, then starts both apps
make dev              # launches backend (port 8000) and frontend (port 5173)
make test             # runs backend pytest suite
make lint             # executes formatters/linters defined in Makefile (if configured)
```

## Docker Workflow

```bash
make setup-env                    # copies backend/.env.example to backend/.env
docker-compose up                 # dev stack with hot reloading
docker-compose -f docker-compose.yml \
               -f docker-compose.prod.yml up --build   # production-like build
```

For production images, set `VITE_API_BASE_URL` before building so the frontend knows where to reach the API.

## Testing

```bash
cd backend
uv run pytest
```

Highlights:

- `tests/test_api.py` exercises `app.api.routes` via FastAPI's TestClient.
- `tests/test_services.py` and `tests/test_agents.py` cover the orchestration layer.
- Provider-specific tests ensure graceful degradation when API keys are missing.

Running the suite regularly is the best way to validate that documentation changes still reflect the current behaviour.
