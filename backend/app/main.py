from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
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
