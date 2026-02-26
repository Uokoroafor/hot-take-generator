# CI/CD Pipeline

The project uses GitHub Actions for continuous integration. The workflow runs on pushes and pull requests to `main` and `dev` branches.

## Pipeline Architecture

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │     │   Backend   │
│    Job      │     │    Job      │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │   (parallel)      │
       └─────────┬─────────┘
                 │
                 ▼
          ┌─────────────┐
          │   Docker    │
          │    Job      │
          └─────────────┘
```

## Jobs

### Frontend Job

Validates the React/TypeScript frontend:

1. **Checkout** - Clone repository
2. **Cache** - Restore `node_modules` and npm cache
3. **Setup Node.js** - Install Node.js 22
4. **Install** - Run `npm install`
5. **Lint** - Run ESLint via `npm run lint`
6. **Test** - Run Vitest coverage suite via `npm run test:coverage`
7. **Upload Coverage** - Store frontend coverage as a build artifact

### Backend Job

Validates the FastAPI backend:

1. **Checkout** - Clone repository
2. **Cache uv** - Restore uv package cache
3. **Cache venv** - Restore Python virtual environment
4. **Setup Python** - Install Python 3.12
5. **Setup uv** - Install uv package manager
6. **Install** - Run `uv sync --frozen`
7. **Lint** - Run ruff via `uvx ruff check .`
8. **Test** - Run pytest coverage with gate via `uv run pytest --cov=app --cov-report=xml --cov-report=term --cov-fail-under=80`
9. **Coverage Badge (main only)** - Generate `backend/coverage.svg` via `genbadge` and push to the `badges` branch
10. **Build docs** - Build MkDocs with `--strict` flag

**Environment Variables:**
- `OPENAI_API_KEY` - From secrets or fallback to fake key
- `ANTHROPIC_API_KEY` - From secrets or fallback to fake key
- `UV_CACHE_DIR` - Cache directory for uv

### Docker Job

Validates multi-stage Docker build (runs only after frontend and backend pass):

1. **Checkout** - Clone repository
2. **Build** - Run `docker compose build` to validate:
   - Builder stage dependency installation
   - Runtime stage image creation
   - Multi-stage artifact copying
   - Non-root user configuration

## Caching Strategy

The pipeline uses aggressive caching to speed up builds:

| Cache | Key | Contents |
| --- | --- | --- |
| Frontend deps | `frontend-{hash of lockfiles}` | `node_modules`, `~/.npm` |
| uv cache | `uv-{hash of pyproject.toml, uv.lock}` | `.uv-cache` |
| Backend venv | `backend-venv-{hash of pyproject.toml, uv.lock}` | `backend/.venv` |

## Secrets

Configure these in GitHub repository settings:

- `OPENAI_API_KEY` - Required for external API tests
- `ANTHROPIC_API_KEY` - Required for external API tests

Tests use fake keys when secrets are unavailable, allowing CI to pass without real API access.

## Triggering Builds

Builds trigger automatically on:
- Push to `main` or `dev`
- Pull request targeting `main` or `dev`

## Local Verification

Run the same checks locally before pushing:

```bash
# Frontend
cd frontend && npm run lint && npm run test:coverage

# Backend
cd backend && uvx ruff check . && uv run pytest --cov=app --cov-report=xml --cov-report=term --cov-fail-under=80 && uv run mkdocs build --strict

# Docker
docker compose build
```
