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

For a full and up-to-date variable list (backend + frontend), see the
[Environment Variables reference](environment-variables.md).

The FastAPI docs are available at `http://localhost:8000/docs` once the server is running.

At runtime, ensure at least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is configured. The `/ready` endpoint returns `503` if both are missing.

## Makefile Shortcuts

From the repo root:

```bash
make quick-start      # installs backend + frontend deps, then starts both apps
make dev              # launches backend (port 8000) and frontend (port 5173)
make test             # runs backend pytest suite
make lint             # executes formatters/linters defined in Makefile (if configured)
```

## Docker Workflow

The backend Dockerfile uses a multi-stage build for production-ready images:

```bash
make setup-env                    # copies backend/.env.example to backend/.env
docker-compose up                 # dev stack with hot reloading
```

**Multi-Stage Build Benefits:**
- Dependencies are installed in a builder stage with build tools
- Runtime stage contains only the app and virtual environment
- Final image runs as non-root user for enhanced security
- Smaller image size (~509MB) compared to single-stage builds

For production images, set `VITE_API_BASE_URL` before building so the frontend knows where to reach the API.

## Inspect Redis Cache (Local Docker)

List cached hot-take keys:

```bash
docker exec hot-take-redis redis-cli --scan --pattern 'hot_take:*'
```

Inspect one key:

```bash
docker exec hot-take-redis redis-cli GET "hot_take:ai:controversial:openai"
docker exec hot-take-redis redis-cli TTL "hot_take:ai:controversial:openai"
```

Pretty-print the cached JSON array:

```bash
docker exec hot-take-redis redis-cli GET "hot_take:ai:controversial:openai" | jq
```

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
