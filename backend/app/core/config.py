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
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
