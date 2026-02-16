import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.base import BaseAgent
from app.agents.openai_agent import OpenAIAgent
from app.agents.anthropic_agent import AnthropicAgent


class TestBaseAgent:
    def test_base_agent_initialization(self):
        class TestAgent(BaseAgent):
            async def generate_hot_take(
                self, topic: str, style: str = "controversial"
            ) -> str:
                return "test"

            def get_system_prompt(self, style: str) -> str:
                return "test prompt"

        agent = TestAgent("Test Agent", "test-model", 0.5)
        assert agent.name == "Test Agent"
        assert agent.model == "test-model"
        assert agent.temperature == 0.5

    def test_base_agent_default_temperature(self):
        class TestAgent(BaseAgent):
            async def generate_hot_take(
                self, topic: str, style: str = "controversial"
            ) -> str:
                return "test"

            def get_system_prompt(self, style: str) -> str:
                return "test prompt"

        agent = TestAgent("Test Agent", "test-model")
        assert agent.temperature == 0.7


class TestOpenAIAgent:
    def test_openai_agent_initialization(self, mock_settings):
        agent = OpenAIAgent()
        assert agent.name == "OpenAI Agent"
        assert agent.model == "gpt-4.1-mini"
        assert agent.temperature == 0.8

    def test_openai_agent_custom_initialization(self, mock_settings):
        agent = OpenAIAgent("Custom Agent", "gpt-4", 0.5)
        assert agent.name == "Custom Agent"
        assert agent.model == "gpt-4"
        assert agent.temperature == 0.5

    def test_get_system_prompt_controversial(self, mock_settings):
        agent = OpenAIAgent()
        prompt = agent.get_system_prompt("controversial")
        assert "provocative" in prompt.lower()
        assert "controversial" in prompt.lower()

    def test_get_system_prompt_sarcastic(self, mock_settings):
        agent = OpenAIAgent()
        prompt = agent.get_system_prompt("sarcastic")
        assert "sarcastic" in prompt.lower()

    def test_get_system_prompt_default(self, mock_settings):
        agent = OpenAIAgent()
        prompt = agent.get_system_prompt("nonexistent_style")
        controversial_prompt = agent.get_system_prompt("controversial")
        assert prompt == controversial_prompt

    @pytest.mark.asyncio
    @patch("app.agents.openai_agent.AsyncOpenAI")
    async def test_generate_hot_take_success(self, mock_openai_class, mock_settings):
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "  AI will dominate the world!  "
        mock_client.chat.completions.create.return_value = mock_response

        agent = OpenAIAgent()
        result = await agent.generate_hot_take(
            "artificial intelligence", "controversial"
        )

        assert result == "AI will dominate the world!"
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4.1-mini"
        assert call_args.kwargs["temperature"] == 0.8
        assert call_args.kwargs["max_tokens"] == 200

    @pytest.mark.asyncio
    @patch("app.agents.openai_agent.AsyncOpenAI")
    async def test_generate_hot_take_api_error(self, mock_openai_class, mock_settings):
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        agent = OpenAIAgent()
        with pytest.raises(RuntimeError, match="OpenAI generation failed"):
            await agent.generate_hot_take("test topic")


class TestAnthropicAgent:
    def test_anthropic_agent_initialization(self, mock_settings):
        agent = AnthropicAgent()
        assert agent.name == "Claude Agent"
        assert agent.model == "claude-haiku-4-5-20251001"
        assert agent.temperature == 0.8

    def test_anthropic_agent_custom_initialization(self, mock_settings):
        agent = AnthropicAgent("Custom Claude", "claude-3-sonnet-20240229", 0.6)
        assert agent.name == "Custom Claude"
        assert agent.model == "claude-3-sonnet-20240229"
        assert agent.temperature == 0.6

    def test_get_system_prompt_analytical(self, mock_settings):
        agent = AnthropicAgent()
        prompt = agent.get_system_prompt("analytical")
        assert "analytical" in prompt.lower()
        assert "analysis" in prompt.lower()

    def test_get_system_prompt_philosophical(self, mock_settings):
        agent = AnthropicAgent()
        prompt = agent.get_system_prompt("philosophical")
        assert "philosophical" in prompt.lower() or "philosopher" in prompt.lower()

    def test_get_system_prompt_default(self, mock_settings):
        agent = AnthropicAgent()
        prompt = agent.get_system_prompt("unknown_style")
        controversial_prompt = agent.get_system_prompt("controversial")
        assert prompt == controversial_prompt

    @pytest.mark.asyncio
    @patch("app.agents.anthropic_agent.AsyncAnthropic")
    async def test_generate_hot_take_success(self, mock_anthropic_class, mock_settings):
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "  Climate change is overrated!  "
        mock_client.messages.create.return_value = mock_response

        agent = AnthropicAgent()
        result = await agent.generate_hot_take("climate change", "contrarian")

        assert result == "Climate change is overrated!"
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-haiku-4-5-20251001"
        assert call_args.kwargs["temperature"] == 0.8
        assert call_args.kwargs["max_tokens"] == 200

    @pytest.mark.asyncio
    @patch("app.agents.anthropic_agent.AsyncAnthropic")
    async def test_generate_hot_take_api_error(
        self, mock_anthropic_class, mock_settings
    ):
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Anthropic API Error")

        agent = AnthropicAgent()
        with pytest.raises(RuntimeError, match="Anthropic generation failed"):
            await agent.generate_hot_take("test topic")


class TestAgentIntegration:
    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_openai_agent_real_api(self, mock_settings):
        if (
            not mock_settings.openai_api_key
            or mock_settings.openai_api_key == "test-openai-key"
        ):
            pytest.skip("No real OpenAI API key provided")

        agent = OpenAIAgent()
        result = await agent.generate_hot_take("pizza", "controversial")

        assert isinstance(result, str)
        assert len(result) > 10
        assert "Error generating hot take" not in result

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_anthropic_agent_real_api(self, mock_settings):
        if (
            not mock_settings.anthropic_api_key
            or mock_settings.anthropic_api_key == "test-anthropic-key"
        ):
            pytest.skip("No real Anthropic API key provided")

        agent = AnthropicAgent()
        result = await agent.generate_hot_take("coffee", "philosophical")

        assert isinstance(result, str)
        assert len(result) > 10
        assert "Error generating hot take" not in result
