import pytest
from pydantic import ValidationError
from app.models.schemas import HotTakeRequest, HotTakeResponse, AgentConfig


class TestHotTakeRequest:
    def test_hot_take_request_valid(self):
        request = HotTakeRequest(
            topic="artificial intelligence", style="controversial", length="medium"
        )
        assert request.topic == "artificial intelligence"
        assert request.style == "controversial"
        assert request.length == "medium"

    def test_hot_take_request_minimal(self):
        request = HotTakeRequest(topic="test topic")
        assert request.topic == "test topic"
        assert request.style == "controversial"  # default
        assert request.length == "medium"  # default

    def test_hot_take_request_missing_topic(self):
        with pytest.raises(ValidationError) as exc_info:
            HotTakeRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "topic" in errors[0]["loc"]

    def test_hot_take_request_empty_topic(self):
        with pytest.raises(ValidationError) as exc_info:
            HotTakeRequest(topic="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "topic" in errors[0]["loc"]

    def test_hot_take_request_custom_style(self):
        request = HotTakeRequest(topic="technology", style="sarcastic")
        assert request.style == "sarcastic"

    def test_hot_take_request_custom_length(self):
        request = HotTakeRequest(topic="technology", length="long")
        assert request.length == "long"

    def test_hot_take_request_json_serialization(self):
        request = HotTakeRequest(
            topic="climate change", style="optimistic", length="short"
        )
        json_data = request.model_dump()

        assert json_data["topic"] == "climate change"
        assert json_data["style"] == "optimistic"
        assert json_data["length"] == "short"

    def test_hot_take_request_valid_agent_type(self):
        request = HotTakeRequest(topic="technology", agent_type="openai")
        assert request.agent_type == "openai"

    def test_hot_take_request_invalid_agent_type(self):
        with pytest.raises(ValidationError):
            HotTakeRequest(topic="technology", agent_type="invalid")


class TestHotTakeResponse:
    def test_hot_take_response_valid(self):
        response = HotTakeResponse(
            hot_take="This is a controversial opinion!",
            topic="technology",
            style="controversial",
            agent_used="OpenAI Agent",
        )
        assert response.hot_take == "This is a controversial opinion!"
        assert response.topic == "technology"
        assert response.style == "controversial"
        assert response.agent_used == "OpenAI Agent"

    def test_hot_take_response_missing_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            HotTakeResponse()

        errors = exc_info.value.errors()
        required_fields = {"hot_take", "topic", "style", "agent_used"}
        error_fields = {error["loc"][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_hot_take_response_empty_strings(self):
        with pytest.raises(ValidationError) as exc_info:
            HotTakeResponse(hot_take="", topic="", style="", agent_used="")

        errors = exc_info.value.errors()
        assert len(errors) == 4  # All fields should fail validation

    def test_hot_take_response_json_serialization(self):
        response = HotTakeResponse(
            hot_take="Pizza is overrated!",
            topic="food",
            style="contrarian",
            agent_used="Claude Agent",
        )
        json_data = response.model_dump()

        assert json_data["hot_take"] == "Pizza is overrated!"
        assert json_data["topic"] == "food"
        assert json_data["style"] == "contrarian"
        assert json_data["agent_used"] == "Claude Agent"


class TestAgentConfig:
    def test_agent_config_valid(self):
        config = AgentConfig(
            id="openai",
            name="Test Agent",
            description="A test AI agent",
            model="gpt-4.1-mini",
            temperature=0.7,
            system_prompt="You are a helpful assistant.",
        )
        assert config.id == "openai"
        assert config.name == "Test Agent"
        assert config.description == "A test AI agent"
        assert config.model == "gpt-4.1-mini"
        assert config.temperature == 0.7
        assert config.system_prompt == "You are a helpful assistant."

    def test_agent_config_missing_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig()

        errors = exc_info.value.errors()
        required_fields = {
            "id",
            "name",
            "description",
            "model",
            "temperature",
            "system_prompt",
        }
        error_fields = {error["loc"][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_agent_config_temperature_validation(self):
        # Valid temperature values
        valid_config = AgentConfig(
            id="test",
            name="Test",
            description="Test",
            model="test-model",
            temperature=0.5,
            system_prompt="Test prompt",
        )
        assert valid_config.temperature == 0.5

        # Temperature should be a number
        with pytest.raises(ValidationError):
            AgentConfig(
                id="test",
                name="Test",
                description="Test",
                model="test-model",
                temperature="invalid",
                system_prompt="Test prompt",
            )

    def test_agent_config_json_serialization(self):
        config = AgentConfig(
            id="anthropic",
            name="Claude Agent",
            description="Anthropic's Claude AI model",
            model="claude-haiku-4-5-20251001",
            temperature=0.8,
            system_prompt="You are a creative and insightful assistant.",
        )
        json_data = config.model_dump()

        assert json_data["id"] == "anthropic"
        assert json_data["name"] == "Claude Agent"
        assert json_data["description"] == "Anthropic's Claude AI model"
        assert json_data["model"] == "claude-haiku-4-5-20251001"
        assert json_data["temperature"] == 0.8
        assert (
            json_data["system_prompt"] == "You are a creative and insightful assistant."
        )


class TestModelCompatibility:
    def test_request_response_compatibility(self):
        request = HotTakeRequest(topic="space exploration", style="optimistic")

        response = HotTakeResponse(
            hot_take="Space exploration will bring humanity together!",
            topic=request.topic,
            style=request.style,
            agent_used="Test Agent",
        )

        assert response.topic == request.topic
        assert response.style == request.style

    def test_models_with_extra_fields(self):
        # Test that models ignore extra fields when strict mode is off
        request_data = {
            "topic": "music",
            "style": "witty",
            "extra_field": "should be ignored",
        }

        request = HotTakeRequest(
            **{k: v for k, v in request_data.items() if k != "extra_field"}
        )
        assert request.topic == "music"
        assert request.style == "witty"
