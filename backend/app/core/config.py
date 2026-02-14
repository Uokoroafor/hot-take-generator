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
    model_config = SettingsConfigDict(env_file=".env")

    def get_cors_origins(self) -> list[str]:
        origins = [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]
        return origins or ["http://localhost:5173"]


settings = Settings()
