import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_openai_agent():
    mock = AsyncMock()
    mock.name = "Test OpenAI Agent"
    mock.model = "gpt-3.5-turbo"
    mock.temperature = 0.8
    mock.generate_hot_take.return_value = "This is a test hot take from OpenAI!"
    return mock


@pytest.fixture
def mock_anthropic_agent():
    mock = AsyncMock()
    mock.name = "Test Anthropic Agent"
    mock.model = "claude-3-haiku-20240307"
    mock.temperature = 0.8
    mock.generate_hot_take.return_value = "This is a test hot take from Anthropic!"
    return mock


@pytest.fixture
def sample_hot_take_request():
    return {
        "topic": "artificial intelligence",
        "style": "controversial",
        "length": "medium",
    }


@pytest.fixture
def sample_hot_take_response():
    return {
        "hot_take": "AI will replace all programmers by 2025!",
        "topic": "artificial intelligence",
        "style": "controversial",
        "agent_used": "Test Agent",
    }


@pytest.fixture
def mock_settings():
    original_openai_key = settings.openai_api_key
    original_anthropic_key = settings.anthropic_api_key

    settings.openai_api_key = "test-openai-key"
    settings.anthropic_api_key = "test-anthropic-key"

    yield settings

    settings.openai_api_key = original_openai_key
    settings.anthropic_api_key = original_anthropic_key
