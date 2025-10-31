# TODOs / Roadmap

A living roadmap for upcoming features, improvements, and refinements to **Hot Take Generator**.  
Each section includes short-term and long-term goals to guide development.

---

## Deployment & Infrastructure

### Short Term
- [ ] Create multi-stage production Dockerfile (builder → slim runtime)
- [ ] Add `.dockerignore` and non-root user
- [ ] Enable health checks and restart policies in `docker-compose.yml`
- [ ] Add `make deploy` target for simplified deployment

### Medium Term
- [ ] Set up production-ready environment variables and config (`ENVIRONMENT=production`, stricter CORS)
- [ ] Add reverse proxy with Nginx or Caddy (TLS, compression)
- [ ] Add deployment workflows:
  - [ ] **Frontend**: Deploy to Vercel or Netlify
  - [ ] **Backend**: Deploy to Fly.io, Render, or Railway
- [ ] Optional: add Helm chart for Kubernetes deployment
- [ ] Add rate limiting and request size limits

---

## Testing & Quality Assurance

### Backend
- [ ] Mock OpenAI and Anthropic APIs with `respx` or `pytest-httpx`
- [ ] Add snapshot (“golden”) tests for generated responses
- [ ] Add property-based tests with Hypothesis for input validation
- [ ] Improve async test coverage, especially in `web_search_service.py`

### Frontend
- [ ] Add component tests using **Vitest + React Testing Library**
- [ ] Add end-to-end tests with **Playwright** (topic input → generated take → result display)
- [ ] Automate tests in CI with coverage thresholds

### General
- [ ] Add mutation testing (`mutmut` for Python, `stryker` for JS)
- [ ] Enforce code coverage ≥ 85% via CI gates
- [ ] Add pre-commit hooks for lint, format, and type-check

---

## Observability & Monitoring

- [ ] Integrate **Langfuse** for AI observability
  - [ ] Track prompt inputs, completions, latency, and provider metrics
  - [ ] Add trace + session IDs to responses
  - [ ] Use Langfuse dashboard to monitor agent performance
- [ ] Evaluate open-source or alternative observability tools:
  - [ ] **Helicone** (LLM observability)
  - [ ] **OpenDevin** or **Prometheus + Grafana**
- [ ] Add structured JSON logging (request IDs, user agent, latency)
- [ ] Add `/health` and `/ready` endpoints for monitoring
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

- [ ] Add loading animation while generating takes
- [ ] Add error states for timeouts, rate limits, invalid input
- [ ] Remember user preferences (style, agent) via localStorage
- [ ] Add dark mode and theming support
- [ ] Add “Share Take” button (copy permalink or tweet)
- [ ] Add analytics for style/agent usage (anonymised)

---

## Developer Experience

- [ ] Add GitHub Actions CI/CD workflows:
  - [ ] Lint → Test → Build → Deploy
  - [ ] Upload coverage to Codecov
- [ ] Add Dependabot or Renovate for dependency updates
- [ ] Add `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`
- [ ] Add issue and PR templates
- [ ] Add changelog following “Keep a Changelog” format

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
