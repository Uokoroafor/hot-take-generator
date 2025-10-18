from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()