# Developer Guide

This guide is for contributors working on the repository locally.

For product-level overview and quick start, use [README.md](./README.md).
For backend architecture and API reference, use the docs site content in `backend/docs/`.

## Local Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+
- Docker + Docker Compose (optional)

### Fastest Start

```bash
git clone https://github.com/Uokoroafor/hot-take-generator.git
cd hot-take-generator
make quick-start
```

### Environment

Create backend env file and add at least one AI provider key:

```bash
make setup-env
```

Required at runtime:

- `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`

Useful optional keys:

- `NEWSAPI_API_KEY`
- `BRAVE_API_KEY`
- `SERPER_API_KEY`
- `REDIS_URL`

For full variable details, see `backend/docs/environment-variables.md`.

## Common Commands

From repository root:

```bash
make dev              # start backend + frontend
make test             # run backend and frontend tests
make lint             # lint backend + frontend
make build            # build frontend
make docker-up        # run with docker compose
make docker-down      # stop docker compose services
make help             # list all commands
```

Backend only:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uv run pytest
```

Frontend only:

```bash
cd frontend
npm install
npm run dev
npm run test:coverage
```

## Testing Expectations

- Add/adjust tests for behaviour changes.
- Keep backend coverage gate passing (`--cov-fail-under=80` in CI).
- Prefer mocking external AI/search calls in unit tests.

## CI Reference

Workflow file: `.github/workflows/main.yaml`

Current CI validates:

1. Frontend lint + coverage tests
2. Backend lint + coverage tests + docs build
3. Docker compose build

See `backend/docs/ci-cd.md` for details.

## Documentation Map

- `README.md`: project overview, quick start, API summary
- `CONTRIBUTING.md`: contribution workflow
- `CHANGELOG.md`: release notes
- `ROADMAP.md`: pragmatic roadmap
- `backend/docs/architecture.md`: backend request flow and internals
- `backend/docs/environment-variables.md`: canonical backend/frontend env var reference
- `backend/docs/backend/api.md`: generated Python API reference
- `backend/docs/search-services.md`: web/news search provider architecture

## Deployment Notes

Current hosting setup:

- Frontend: Vercel
- Backend: Render

Keep docs and environment settings aligned when deployment changes.
