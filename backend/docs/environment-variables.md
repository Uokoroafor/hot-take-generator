# Environment Variables

This is the canonical reference for environment variables used by the project.

## Backend (`backend/.env`)

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | No* | unset | Enables OpenAI agent. |
| `ANTHROPIC_API_KEY` | No* | unset | Enables Anthropic agent. |
| `ENVIRONMENT` | No | `development` | Runtime environment label. |
| `DEBUG` | No | `true` | Enables debug-mode behaviour. |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Comma-separated allowed frontend origins. |
| `GENERATE_RATE_LIMIT_PER_MINUTE` | No | `30` | Per-IP generation rate limit. |
| `MAX_GENERATE_REQUEST_BYTES` | No | `16384` | Max request body size for generation endpoint. |
| `TRUST_X_FORWARDED_FOR` | No | `true` | Trust proxy IP headers (useful on Render). |
| `REDIS_URL` | No | unset | Enables Redis caching when set. |
| `CACHE_TTL_SECONDS` | No | `86400` | TTL for cached keys (seconds). |
| `CACHE_VARIANT_POOL_SIZE` | No | `5` | Number of response variants kept per cache key. |
| `LANGFUSE_TRACING_ENABLED` | No | `true` | Enables/disables Langfuse instrumentation. |
| `LANGFUSE_PUBLIC_KEY` | No | unset | Langfuse public key. |
| `LANGFUSE_SECRET_KEY` | No | unset | Langfuse secret key. |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse API host. |
| `LANGFUSE_BASE_URL` | No | unset | Backward-compatible alias for Langfuse host. |
| `LANGFUSE_TRACING_ENVIRONMENT` | No | unset | Environment tag attached to traces. |
| `NEWSAPI_API_KEY` | No | unset | Enables news search context. |
| `BRAVE_API_KEY` | No | unset | Enables Brave web search provider. |
| `SERPER_API_KEY` | No | unset | Enables Serper web search provider. |
| `SEARCH_NEWS_DAYS_DEFAULT` | No | `14` | Default recency window for news search. |
| `SEARCH_DOMAIN_ALLOWLIST` | No | empty | Optional CSV list to include only specific domains. |
| `SEARCH_DOMAIN_BLOCKLIST` | No | empty | Optional CSV list to exclude specific domains. |
| `SEARCH_TRUSTED_DOMAINS` | No | prefilled CSV | Domains given a ranking boost in search scoring. |
| `SEARCH_SCORE_WEIGHT_RELEVANCE` | No | `0.60` | Relevance weight in search score. |
| `SEARCH_SCORE_WEIGHT_RECENCY` | No | `0.20` | Recency weight in search score. |
| `SEARCH_SCORE_WEIGHT_SNIPPET` | No | `0.10` | Snippet-quality weight in search score. |
| `SEARCH_SCORE_WEIGHT_DOMAIN` | No | `0.10` | Trusted-domain weight in search score. |
| `SEARCH_SCORE_STRICT_NO_OVERLAP_PENALTY` | No | `0.35` | Penalty factor when topic overlap is weak. |

\* At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be set for the app to be ready (`/ready`).

## Frontend (`frontend/.env`)

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | Yes | `http://localhost:8000` | Base URL for backend API requests from the frontend. |

## Deployment Notes

- On **Vercel**, set `VITE_API_BASE_URL` to your deployed backend URL.
- On **Render**, set backend keys (`OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`) plus any optional provider keys.
- Keep local `.env` values aligned with production settings where behavior should match.
