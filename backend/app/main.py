import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(
    title="Hot Take Generator API",
    description="A FastAPI backend for generating hot takes using LLM agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory limiter is sufficient for single-instance personal deployments.
rate_limit_window_seconds = 60
request_timestamps_by_ip: dict[str, deque[float]] = defaultdict(deque)


def get_client_ip(request: Request) -> str:
    if settings.trust_x_forwarded_for:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.middleware("http")
async def basic_rate_limit(request: Request, call_next):
    if request.url.path == "/api/generate" and request.method.upper() == "POST":
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.max_generate_request_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": "Request payload too large for /api/generate."
                        },
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header."},
                )

        now = time.time()
        client_ip = get_client_ip(request)
        timestamps = request_timestamps_by_ip[client_ip]

        while timestamps and now - timestamps[0] > rate_limit_window_seconds:
            timestamps.popleft()

        if len(timestamps) >= settings.generate_rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please wait before generating again."
                },
            )

        timestamps.append(now)

    return await call_next(request)


app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hot Take Generator API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check(response: Response):
    """
    Readiness probe that verifies required environment configuration.
    Returns 200 if the service is ready to handle requests, 503 otherwise.
    """
    missing_config = []

    # Check that at least one AI provider is configured
    if not settings.openai_api_key and not settings.anthropic_api_key:
        missing_config.append(
            "At least one AI provider API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required"
        )

    if missing_config:
        response.status_code = 503
        return {"status": "not_ready", "missing_configuration": missing_config}

    return {"status": "ready"}
