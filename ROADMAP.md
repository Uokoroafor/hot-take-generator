# Roadmap

A focused roadmap for practical improvements to **Hot Take Generator**.
This list intentionally prioritises high-ROI work for a personal project.

---

## Deployment & Infrastructure

### Short Term
- [x] Create multi-stage production Dockerfile (builder -> slim runtime) - _Multi-stage build implemented with builder and runtime stages, non-root user, and optimised for production_
- [x] Add `.dockerignore` and non-root user - _`.dockerignore` added to backend and frontend_
- [x] Enable health checks and restart policies in `docker-compose.yml` - _Health checks and `restart: unless-stopped` configured_
- [x] Set up production-ready environment variables and config (`ENVIRONMENT=production`, stricter CORS) - _Environment variable support added_
- [x] Add deployment workflows:
  - [x] **Frontend**: Deploy to Vercel or Netlify - _Frontend deployed to Vercel_
  - [x] **Backend**: Deploy to Fly.io, Render, or Railway - _Backend deployed to Render_
- [x] Add rate limiting and request size limits - _Per-IP rate limiting and max request payload checks added to `/api/generate`_

---

## Testing & Quality Assurance

### Backend
- [ ] Mock OpenAI and Anthropic APIs with `respx` or `pytest-httpx`
- [ ] Add snapshot ("golden") tests for generated responses
- [ ] Improve async test coverage, especially in `web_search_service.py`

### Frontend
- [x] Add component tests using **Vitest + React Testing Library** - _Comprehensive test suites for HotTakeGenerator and App components (20 tests total)_
- [x] Automate tests in CI with coverage thresholds - _Backend enforces 80% minimum via pytest; frontend enforces 70% minimum via Vitest coverage thresholds_

### General
- [x] Achieve code coverage ≥ 85% - _Backend at 85% total coverage, frontend has 20 comprehensive tests_
- [x] Enforce backend code coverage ≥ 80% via CI gates - _GitHub Actions backend pytest now fails under 80% with `--cov-fail-under=80`_
- [x] Add pre-commit hooks for lint, format, and type-check - _Comprehensive pre-commit config with Ruff, ESLint, TypeScript checks, and file validation_

---

## Observability & Monitoring

- [x] Integrate **Langfuse** for AI observability - _Langfuse client integration added with graceful fallback when unconfigured_
  - [x] Track prompt inputs, completions, latency, and provider metrics - _Request spans and generation observations wired into `/api/generate` flow_
  - [x] Add trace + session IDs to responses - _Trace ID returned via `X-Trace-Id` response header when available_
  - [x] Use Langfuse dashboard to monitor agent performance
- [x] Add `/health` endpoint for monitoring - _Health check endpoint implemented in backend_
- [x] Add `/ready` endpoint for monitoring - _Readiness endpoint implemented with comprehensive tests for API key configurations_

---

## AI Features & Agents

- [ ] Add adjustable take hotness ("spice level") control in UI - _User-facing intensity control for how provocative the take should be; not raw LLM sampling temperature_
- [x] Add streaming token responses (SSE) - _POST /api/generate/stream endpoint with status/sources/token/done/error events; frontend useStreamingGenerate hook; live cursor during generation_
- [x] Include source URLs and timestamps in generated takes - _Structured `sources` records now include URL and optional publish timestamp_

---

## Frontend & UX

- [x] Add loading animation while generating takes - _Loading states with skeleton UI implemented_
- [x] Add error states for timeouts, rate limits, invalid input - _Error handling with toast notifications_
- [x] Remember user preferences (style, agent) via localStorage - _Dark mode and saved takes stored in localStorage_
- [x] Add dark mode and theming support - _Full dark mode with system preference detection_
- [x] Add "Share Take" button (copy permalink or tweet) - _Copy to clipboard and share to X/Twitter functionality_
- [x] Add multiple pages for better UX - _History, Styles, Agents, Sources, Settings, and About pages with navigation_
- [ ] Wire up Style Presets page — integrate with HotTakeGenerator and backend so custom presets (tone, length, emojis) affect generation
- [ ] Add text-to-speech playback for generated takes — Web Speech API (free, browser-native) or OpenAI TTS for higher quality

---

## Developer Experience

- [x] Add GitHub Actions CI/CD workflows - _Frontend (lint, test), Backend (ruff, pytest), Docker build checks_
  - [x] Lint -> Test -> Build workflow implemented
  - [x] Deploy step - _Render and Vercel auto-deploy from connected branches_
- [x] Add Dependabot for dependency updates - _Configured for backend (pip), frontend (npm), GitHub Actions, and Docker_
- [x] Add `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` - _Community contribution and conduct docs added_
- [x] Add issue and PR templates - _Pull request template added_
- [x] Add changelog following "Keep a Changelog" format - _`CHANGELOG.md` now follows Keep a Changelog with version links_

---

## Documentation & Project Polish

- [x] Add architecture diagram (frontend ↔ backend ↔ agents ↔ web search) - _Documented in `backend/docs/architecture.md`_
- [x] Add environment variables reference table (single canonical location) - _Canonical reference added at `backend/docs/environment-variables.md` and linked from README/docs_
- [ ] Add screenshots / demo GIF to README

---
