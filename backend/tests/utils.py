import asyncio
from typing import Any, Dict, List
from unittest.mock import MagicMock


class MockAgent:
    """Mock agent for testing purposes"""

    def __init__(self, name: str, responses: List[str] = None):
        self.name = name
        self.model = "mock-model"
        self.temperature = 0.7
        self.responses = responses or ["Mock hot take response"]
        self.call_count = 0

    async def generate_hot_take(self, topic: str, style: str = "controversial") -> str:
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

    def get_system_prompt(self, style: str) -> str:
        return f"Mock system prompt for {style} style"


def create_mock_response(
    hot_take: str, topic: str, style: str, agent_name: str
) -> Dict[str, Any]:
    """Create a mock API response"""
    return {
        "hot_take": hot_take,
        "topic": topic,
        "style": style,
        "agent_used": agent_name,
    }


def create_mock_openai_response(content: str) -> MagicMock:
    """Create a mock OpenAI API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


def create_mock_anthropic_response(content: str) -> MagicMock:
    """Create a mock Anthropic API response"""
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = content
    return mock_response


class AsyncContextManager:
    """Helper for testing async context managers"""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def run_async_test(coro):
    """Helper to run async tests in sync test functions"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestDataFactory:
    """Factory for creating test data"""

    @staticmethod
    def hot_take_request(topic="test topic", style="controversial", length="medium"):
        return {"topic": topic, "style": style, "length": length}

    @staticmethod
    def hot_take_response(
        hot_take="Test hot take",
        topic="test topic",
        style="controversial",
        agent_used="Test Agent",
    ):
        return {
            "hot_take": hot_take,
            "topic": topic,
            "style": style,
            "agent_used": agent_used,
        }

    @staticmethod
    def agent_config(
        name="Test Agent",
        description="A test agent",
        model="test-model",
        temperature=0.7,
        system_prompt="Test system prompt",
    ):
        return {
            "name": name,
            "description": description,
            "model": model,
            "temperature": temperature,
            "system_prompt": system_prompt,
        }


def assert_response_format(response_data: Dict[str, Any]):
    """Assert that a response has the correct format"""
    required_fields = {"hot_take", "topic", "style", "agent_used"}
    assert all(field in response_data for field in required_fields), (
        f"Response missing required fields. Expected: {required_fields}, Got: {response_data.keys()}"
    )

    assert isinstance(response_data["hot_take"], str), "hot_take should be a string"
    assert isinstance(response_data["topic"], str), "topic should be a string"
    assert isinstance(response_data["style"], str), "style should be a string"
    assert isinstance(response_data["agent_used"], str), "agent_used should be a string"

    assert len(response_data["hot_take"]) > 0, "hot_take should not be empty"
    assert len(response_data["topic"]) > 0, "topic should not be empty"
    assert len(response_data["style"]) > 0, "style should not be empty"
    assert len(response_data["agent_used"]) > 0, "agent_used should not be empty"


class MockAPIClient:
    """Mock API client for testing external API calls"""

    def __init__(self, responses: List[str] = None, should_fail: bool = False):
        self.responses = responses or ["Mock API response"]
        self.should_fail = should_fail
        self.call_count = 0
        self.call_history = []

    async def create_completion(self, **kwargs):
        self.call_history.append(kwargs)

        if self.should_fail:
            raise Exception("Mock API error")

        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1

        return create_mock_openai_response(response)

    async def create_message(self, **kwargs):
        self.call_history.append(kwargs)

        if self.should_fail:
            raise Exception("Mock API error")

        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1

        return create_mock_anthropic_response(response)
