# TODOs / Roadmap

A living roadmap for upcoming features, improvements, and refinements to **Hot Take Generator**.
Each section includes short-term and long-term goals to guide development.

---

## Deployment & Infrastructure

### Short Term
- [x] Create multi-stage production Dockerfile (builder -> slim runtime) - _Multi-stage build implemented with builder and runtime stages, non-root user, and optimised for production_
- [x] Add `.dockerignore` and non-root user - _`.dockerignore` added to backend and frontend_
- [x] Enable health checks and restart policies in `docker-compose.yml` - _Health checks and `restart: unless-stopped` configured_
- [ ] Add `make deploy` target for simplified deployment

### Medium Term
- [x] Set up production-ready environment variables and config (`ENVIRONMENT=production`, stricter CORS) - _Environment variable support added_
- [ ] Add reverse proxy with Nginx or Caddy (TLS, compression)
- [ ] Add deployment workflows:
  - [x] **Frontend**: Deploy to Vercel or Netlify - _Frontend deployed to Vercel_
  - [x] **Backend**: Deploy to Fly.io, Render, or Railway - _Backend deployed to Render_
- [ ] Optional: add Helm chart for Kubernetes deployment
- [x] Add rate limiting and request size limits - _Per-IP rate limiting and max request payload checks added to `/api/generate`_

---

## Testing & Quality Assurance

### Backend
- [ ] Mock OpenAI and Anthropic APIs with `respx` or `pytest-httpx`
- [ ] Add snapshot ("golden") tests for generated responses
- [ ] Add property-based tests with Hypothesis for input validation
- [ ] Improve async test coverage, especially in `web_search_service.py`

### Frontend
- [x] Add component tests using **Vitest + React Testing Library** - _Comprehensive test suites for HotTakeGenerator and App components (20 tests total)_
- [ ] Add end-to-end tests with **Playwright** (topic input -> generated take -> result display)
- [ ] Automate tests in CI with coverage thresholds - _Tests run in CI, coverage thresholds need to be added_

### General
- [ ] Add mutation testing (`mutmut` for Python, `stryker` for JS)
- [x] Achieve code coverage ≥ 85% - _Backend at 85% total coverage, frontend has 20 comprehensive tests_
- [ ] Enforce code coverage ≥ 85% via CI gates - _Coverage achieved, needs CI enforcement_
- [x] Add pre-commit hooks for lint, format, and type-check - _Comprehensive pre-commit config with Ruff, ESLint, TypeScript checks, and file validation_

---

## Observability & Monitoring

- [x] Integrate **Langfuse** for AI observability - _Langfuse client integration added with graceful fallback when unconfigured_
  - [x] Track prompt inputs, completions, latency, and provider metrics - _Request spans and generation observations wired into `/api/generate` flow_
  - [x] Add trace + session IDs to responses - _Trace ID returned via `X-Trace-Id` response header when available_
  - [ ] Use Langfuse dashboard to monitor agent performance
- [ ] Evaluate open-source or alternative observability tools:
  - [ ] **Helicone** (LLM observability)
  - [ ] **OpenDevin** or **Prometheus + Grafana**
- [ ] Add structured JSON logging (request IDs, user agent, latency)
- [x] Add `/health` endpoint for monitoring - _Health check endpoint implemented in backend_
- [x] Add `/ready` endpoint for monitoring - _Readiness endpoint implemented with comprehensive tests for API key configurations_
- [ ] Add OpenTelemetry tracing for backend routes
- [ ] Add metrics exporter (Prometheus format)

---

## AI Features & Agents

- [ ] Support additional LLM providers (Mistral, Gemini)
- [ ] Add adjustable creativity/temperature settings in UI
- [ ] Add streaming token responses (SSE or WebSocket)
- [ ] Cache web search results with Redis
- [ ] Include source URLs and timestamps in generated takes
- [ ] Add prompt safety filters (max tokens, banned phrases)

---

## Frontend & UX

- [x] Add loading animation while generating takes - _Loading states with skeleton UI implemented_
- [x] Add error states for timeouts, rate limits, invalid input - _Error handling with toast notifications_
- [x] Remember user preferences (style, agent) via localStorage - _Dark mode and saved takes stored in localStorage_
- [x] Add dark mode and theming support - _Full dark mode with system preference detection_
- [x] Add "Share Take" button (copy permalink or tweet) - _Copy to clipboard and share to X/Twitter functionality_
- [x] Add multiple pages for better UX - _History, Styles, Agents, Sources, Settings, and About pages with navigation_
- [ ] Wire up Style Presets page — integrate with HotTakeGenerator and backend so custom presets (tone, length, emojis) affect generation
- [ ] Add analytics for style/agent usage (anonymised)

---

## Developer Experience

- [x] Add GitHub Actions CI/CD workflows - _Frontend (lint, test), Backend (ruff, pytest), Docker build checks_
  - [x] Lint -> Test -> Build workflow implemented
  - [ ] Deploy step
  - [ ] Upload coverage to Codecov
- [x] Add Dependabot for dependency updates - _Configured for backend (pip), frontend (npm), GitHub Actions, and Docker_
- [x] Add `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` - _Community contribution and conduct docs added_
- [x] Add issue and PR templates - _Pull request template added_
- [ ] Add changelog following "Keep a Changelog" format

---

## Documentation & Project Polish

- [ ] Add architecture diagram (frontend ↔ backend ↔ agents ↔ web search)
- [ ] Add environment variables reference table
- [ ] Add screenshots / demo GIF to README
- [ ] Add FAQ section (e.g. “Why do takes repeat?”)
- [ ] Add LICENSE badge and CI status badges to README
- [ ] Write blog-style “Building the Hot Take Generator” post

---

## Stretch Goals

- [ ] Multi-user sessions with authentication
- [ ] Save and browse “best takes” leaderboard
- [ ] Integrate voice generation (TTS) for podcast-style output
- [ ] Browser extension or Discord bot interface
- [ ] Mobile-friendly PWA (offline support)

---

_This roadmap evolves as development continues.
Contributions, ideas, and spicy opinions are always welcome!_
