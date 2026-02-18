from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    environment: str = "development"
    debug: bool = True
    # News search API
    newsapi_api_key: Optional[str] = None
    # Web search APIs
    brave_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    # CORS configuration (comma-separated origins)
    cors_origins: str = "http://localhost:5173"
    # Basic rate limiting for generation endpoint
    generate_rate_limit_per_minute: int = 30
    # Max request body size (bytes) for generation endpoint
    max_generate_request_bytes: int = 16_384
    # Trust proxy header for client IP (recommended on Render)
    trust_x_forwarded_for: bool = True
    # Langfuse tracing
    langfuse_tracing_enabled: bool = True
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    # Backward compatibility for existing env naming
    langfuse_base_url: Optional[str] = None
    langfuse_tracing_environment: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_cors_origins(self) -> list[str]:
        origins = [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]
        return origins or ["http://localhost:5173"]


settings = Settings()
