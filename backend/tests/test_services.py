import pytest
from unittest.mock import AsyncMock, patch
from app.services.hot_take_service import HotTakeService
from app.models.schemas import HotTakeResponse


class TestHotTakeService:
    def test_service_initialization(self):
        service = HotTakeService()
        assert "openai" in service.agents
        assert "anthropic" in service.agents
        assert len(service.agents) == 2

    def test_get_available_agents(self):
        service = HotTakeService()
        agents = service.get_available_agents()
        assert isinstance(agents, list)
        assert "openai" in agents
        assert "anthropic" in agents

    def test_get_available_styles(self):
        service = HotTakeService()
        styles = service.get_available_styles()
        assert isinstance(styles, list)
        expected_styles = [
            "controversial",
            "sarcastic",
            "optimistic",
            "pessimistic",
            "absurd",
            "analytical",
            "philosophical",
            "witty",
            "contrarian",
        ]
        for style in expected_styles:
            assert style in styles

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_generate_hot_take_with_specific_agent(
        self, mock_anthropic, mock_openai
    ):
        mock_openai_instance = AsyncMock()
        mock_openai_instance.name = "OpenAI Agent"
        mock_openai_instance.generate_hot_take.return_value = "OpenAI hot take!"
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic_instance.name = "Anthropic Agent"
        mock_anthropic_instance.generate_hot_take.return_value = "Anthropic hot take!"
        mock_anthropic.return_value = mock_anthropic_instance

        service = HotTakeService()
        result = await service.generate_hot_take(
            topic="test topic", style="controversial", agent_type="openai"
        )

        assert isinstance(result, HotTakeResponse)
        assert result.hot_take == "OpenAI hot take!"
        assert result.topic == "test topic"
        assert result.style == "controversial"
        assert result.agent_used == "OpenAI Agent"
        mock_openai_instance.generate_hot_take.assert_called_once_with(
            "test topic", "controversial", None
        )

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_generate_hot_take_with_anthropic_agent(
        self, mock_anthropic, mock_openai
    ):
        mock_openai_instance = AsyncMock()
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic_instance.name = "Anthropic Agent"
        mock_anthropic_instance.generate_hot_take.return_value = "Anthropic hot take!"
        mock_anthropic.return_value = mock_anthropic_instance

        service = HotTakeService()
        result = await service.generate_hot_take(
            topic="artificial intelligence",
            style="philosophical",
            agent_type="anthropic",
        )

        assert isinstance(result, HotTakeResponse)
        assert result.hot_take == "Anthropic hot take!"
        assert result.topic == "artificial intelligence"
        assert result.style == "philosophical"
        assert result.agent_used == "Anthropic Agent"
        mock_anthropic_instance.generate_hot_take.assert_called_once_with(
            "artificial intelligence", "philosophical", None
        )

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.random.choice")
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_generate_hot_take_random_agent(
        self, mock_anthropic, mock_openai, mock_random_choice
    ):
        mock_openai_instance = AsyncMock()
        mock_openai_instance.name = "OpenAI Agent"
        mock_openai_instance.generate_hot_take.return_value = "Random agent hot take!"
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic.return_value = mock_anthropic_instance

        mock_random_choice.return_value = mock_openai_instance

        service = HotTakeService()
        result = await service.generate_hot_take(topic="random topic", style="absurd")

        assert isinstance(result, HotTakeResponse)
        assert result.hot_take == "Random agent hot take!"
        assert result.agent_used == "OpenAI Agent"
        mock_random_choice.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_generate_hot_take_invalid_agent_type(
        self, mock_anthropic, mock_openai
    ):
        mock_openai_instance = AsyncMock()
        mock_openai_instance.name = "OpenAI Agent"
        mock_openai_instance.generate_hot_take.return_value = "Fallback hot take!"
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic_instance.name = "Anthropic Agent"
        mock_anthropic.return_value = mock_anthropic_instance

        service = HotTakeService()

        # Mock random.choice to return a specific agent
        with patch(
            "app.services.hot_take_service.random.choice",
            return_value=mock_openai_instance,
        ):
            result = await service.generate_hot_take(
                topic="test topic", style="controversial", agent_type="invalid_agent"
            )

        assert isinstance(result, HotTakeResponse)
        assert result.hot_take == "Fallback hot take!"

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_generate_hot_take_default_style(self, mock_anthropic, mock_openai):
        mock_openai_instance = AsyncMock()
        mock_openai_instance.name = "OpenAI Agent"
        mock_openai_instance.generate_hot_take.return_value = "Default style hot take!"
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic.return_value = mock_anthropic_instance

        service = HotTakeService()
        result = await service.generate_hot_take(
            topic="test topic", agent_type="openai"
        )

        assert isinstance(result, HotTakeResponse)
        assert result.style == "controversial"  # default style
        mock_openai_instance.generate_hot_take.assert_called_once_with(
            "test topic", "controversial", None
        )

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_generate_hot_take_agent_error_handling(
        self, mock_anthropic, mock_openai
    ):
        mock_openai_instance = AsyncMock()
        mock_openai_instance.name = "OpenAI Agent"
        mock_openai_instance.generate_hot_take.side_effect = Exception("Agent failed")
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic.return_value = mock_anthropic_instance

        service = HotTakeService()

        # The service should propagate the exception
        with pytest.raises(Exception, match="Agent failed"):
            await service.generate_hot_take(topic="test topic", agent_type="openai")


class TestServiceIntegration:
    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_service_agent_interaction(self, mock_anthropic, mock_openai):
        mock_openai_instance = AsyncMock()
        mock_openai_instance.name = "OpenAI Agent"
        mock_openai_instance.generate_hot_take.return_value = (
            "Integration test hot take!"
        )
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic_instance.name = "Anthropic Agent"
        mock_anthropic.return_value = mock_anthropic_instance

        service = HotTakeService()

        # Test multiple calls
        for style in ["controversial", "sarcastic", "optimistic"]:
            result = await service.generate_hot_take(
                topic=f"test topic {style}", style=style, agent_type="openai"
            )
            assert result.style == style
            assert result.topic == f"test topic {style}"

        assert mock_openai_instance.generate_hot_take.call_count == 3

    @pytest.mark.asyncio
    async def test_service_with_real_agents(self):
        service = HotTakeService()

        # Verify agents are properly initialized
        assert hasattr(service.agents["openai"], "generate_hot_take")
        assert hasattr(service.agents["anthropic"], "generate_hot_take")

        # Verify agent names
        assert service.agents["openai"].name == "OpenAI Agent"
        assert service.agents["anthropic"].name == "Claude Agent"
