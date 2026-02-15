import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from app.services.web_search_service import WebSearchService
from app.models.schemas import HotTakeResponse


class TestNewWebSearchService:
    """Tests for the new flexible web search service."""

    def test_web_search_service_initialization_with_provider(self):
        """Test service initializes with a specific provider."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_settings:
            mock_settings.brave_api_key = "test_key"
            service = WebSearchService(provider_name="brave")
            assert service.provider is not None
            assert service.provider.name == "brave"

    def test_web_search_service_auto_select_provider(self):
        """Test service auto-selects first configured provider."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_brave:
            with patch(
                "app.services.search_providers.serper_provider.settings"
            ) as mock_serper:
                mock_brave.brave_api_key = "test_brave_key"
                mock_serper.serper_api_key = None
                service = WebSearchService()
                assert service.provider is not None
                assert service.provider.name == "brave"

    def test_web_search_service_no_configured_providers(self):
        """Test service handles no configured providers."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_brave:
            with patch(
                "app.services.search_providers.serper_provider.settings"
            ) as mock_serper:
                mock_brave.brave_api_key = None
                mock_serper.serper_api_key = None
                service = WebSearchService()
                assert service.provider is None

    @pytest.mark.asyncio
    async def test_web_search_no_provider(self):
        """Test search returns empty when no provider configured."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_brave:
            with patch(
                "app.services.search_providers.serper_provider.settings"
            ) as mock_serper:
                mock_brave.brave_api_key = None
                mock_serper.serper_api_key = None
                service = WebSearchService()
                results = await service.search("test query", max_results=5)
                assert results == []

    @pytest.mark.asyncio
    async def test_web_search_with_provider_success(self):
        """Test successful web search with provider."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_settings:
            mock_settings.brave_api_key = "test_key"
            service = WebSearchService(provider_name="brave")

            mock_results = [
                {
                    "title": "Test Result",
                    "url": "https://example.com/test",
                    "snippet": "Test snippet",
                    "source": "example.com",
                    "published": None,
                }
            ]

            with patch.object(service.provider, "search", return_value=mock_results):
                results = await service.search("test query", max_results=5)
                assert len(results) == 1
                assert results[0]["title"] == "Test Result"

    def test_format_search_context_empty(self):
        """Test formatting with no results."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_settings:
            mock_settings.brave_api_key = None
            service = WebSearchService()
            context = service.format_search_context([])
            assert "No web search results found" in context

    def test_format_search_context_with_results(self):
        """Test formatting with results."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_settings:
            mock_settings.brave_api_key = "test_key"
            service = WebSearchService()

            results = [
                {
                    "title": "Web Result 1",
                    "snippet": "Test snippet 1",
                    "source": "example.com",
                    "url": "https://example.com/page1",
                    "published": datetime.now(timezone.utc),
                },
                {
                    "title": "Web Result 2",
                    "snippet": "Test snippet 2",
                    "source": "test.org",
                    "url": "https://test.org/page2",
                    "published": None,
                },
            ]

            context = service.format_search_context(results)

            assert "Web search results:" in context
            assert "Web Result 1" in context
            assert "example.com" in context
            assert "Web Result 2" in context
            assert "test.org" in context
            assert "https://example.com/page1" in context

    def test_get_available_providers(self):
        """Test getting available provider names."""
        service = WebSearchService()
        providers = service.get_available_providers()
        assert "brave" in providers
        assert "serper" in providers

    def test_get_configured_providers(self):
        """Test getting configured provider names."""
        with patch(
            "app.services.search_providers.brave_provider.settings"
        ) as mock_brave:
            with patch(
                "app.services.search_providers.serper_provider.settings"
            ) as mock_serper:
                mock_brave.brave_api_key = "test_key"
                mock_serper.serper_api_key = None
                service = WebSearchService()
                configured = service.get_configured_providers()
                assert "brave" in configured
                assert "serper" not in configured


class TestWebSearchIntegration:
    """Test web search integration with the hot take service"""

    @pytest.mark.asyncio
    async def test_hot_take_service_with_web_search(self):
        """Test hot take service with web search enabled."""
        from app.services.hot_take_service import HotTakeService

        service = HotTakeService()

        mock_results = [
            {
                "title": "Web Result 1",
                "url": "https://example.com/web-result-1",
                "snippet": "AI technology advances",
                "source": "example.com",
                "published": None,
            }
        ]
        with patch.object(
            service.web_search_service, "search", return_value=mock_results
        ):
            # Mock the agent response
            with patch.object(
                service.agents["openai"],
                "generate_hot_take",
                return_value="AI hot take",
            ):
                result = await service.generate_hot_take(
                    topic="AI",
                    style="controversial",
                    agent_type="openai",
                    use_web_search=True,
                    max_articles=2,
                )

                assert isinstance(result, HotTakeResponse)
                assert result.web_search_used is True
                assert result.news_context is not None
                assert result.sources is not None
                assert len(result.sources) == 1
                assert result.sources[0].type == "web"
                assert result.sources[0].title == "Web Result 1"

    @pytest.mark.asyncio
    async def test_hot_take_service_web_search_disabled(self):
        """Test hot take service with web search disabled."""
        from app.services.hot_take_service import HotTakeService

        service = HotTakeService()

        # Mock the agent response
        with patch.object(
            service.agents["openai"], "generate_hot_take", return_value="AI hot take"
        ):
            result = await service.generate_hot_take(
                topic="AI",
                style="controversial",
                agent_type="openai",
                use_web_search=False,
            )

            assert isinstance(result, HotTakeResponse)
            assert result.web_search_used is False
            assert result.news_context is None
            assert result.sources is None

    @pytest.mark.asyncio
    async def test_hot_take_service_web_search_error(self):
        """Test hot take service continues when web search fails."""
        from app.services.hot_take_service import HotTakeService

        service = HotTakeService()

        # Mock web search to raise an error
        with patch.object(
            service.web_search_service,
            "search",
            side_effect=Exception("Search failed"),
        ):
            # Mock the agent response
            with patch.object(
                service.agents["openai"],
                "generate_hot_take",
                return_value="AI hot take",
            ):
                result = await service.generate_hot_take(
                    topic="AI",
                    style="controversial",
                    agent_type="openai",
                    use_web_search=True,
                )

                # Should continue without web search when it fails
                assert isinstance(result, HotTakeResponse)
                assert result.web_search_used is False
                assert result.sources is None


class TestWebSearchModels:
    """Test the updated models with web search fields"""

    def test_hot_take_request_with_web_search(self):
        """Test HotTakeRequest with web search parameters."""
        from app.models.schemas import HotTakeRequest

        request = HotTakeRequest(
            topic="test", style="controversial", use_web_search=True, max_articles=5
        )

        assert request.topic == "test"
        assert request.use_web_search is True
        assert request.max_articles == 5

    def test_hot_take_request_defaults(self):
        """Test HotTakeRequest default values."""
        from app.models.schemas import HotTakeRequest

        request = HotTakeRequest(topic="test")

        assert request.use_web_search is False
        assert request.use_news_search is False
        assert request.max_articles == 3
        assert request.web_search_provider is None

    def test_hot_take_request_with_provider(self):
        """Test HotTakeRequest with specific provider."""
        from app.models.schemas import HotTakeRequest

        request = HotTakeRequest(
            topic="test",
            use_web_search=True,
            web_search_provider="brave",
        )

        assert request.web_search_provider == "brave"

    def test_hot_take_request_invalid_provider(self):
        """Test HotTakeRequest with invalid provider."""
        from app.models.schemas import HotTakeRequest

        with pytest.raises(ValueError):
            HotTakeRequest(
                topic="test",
                use_web_search=True,
                web_search_provider="invalid",
            )

    def test_hot_take_response_with_web_search(self):
        """Test HotTakeResponse with web search data."""
        response = HotTakeResponse(
            hot_take="test take",
            topic="test",
            style="controversial",
            agent_used="Test Agent",
            web_search_used=True,
            news_context="Test news context",
            sources=[
                {
                    "type": "web",
                    "title": "Example",
                    "url": "https://example.com",
                    "snippet": "Snippet",
                }
            ],
        )

        assert response.web_search_used is True
        assert response.news_context == "Test news context"
        assert response.sources is not None
        assert response.sources[0].type == "web"

    def test_hot_take_response_without_web_search(self):
        """Test HotTakeResponse without web search."""
        response = HotTakeResponse(
            hot_take="test take",
            topic="test",
            style="controversial",
            agent_used="Test Agent",
        )

        assert response.web_search_used is False
        assert response.news_context is None


class TestWebSearchExternalIntegration:
    """Tests that require external API access - run with pytest -m external"""

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_real_brave_search(self):
        """Test with real Brave API - requires API key and internet connection."""
        service = WebSearchService(provider_name="brave")

        if not service.provider or not service.provider.is_configured():
            pytest.skip("Brave API key not configured")

        results = await service.search("technology news", max_results=3)

        assert isinstance(results, list)
        if results:  # May be empty due to rate limits
            assert "title" in results[0]
            assert "url" in results[0]
            assert "snippet" in results[0]

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_real_serper_search(self):
        """Test with real Serper API - requires API key and internet connection."""
        service = WebSearchService(provider_name="serper")

        if not service.provider or not service.provider.is_configured():
            pytest.skip("Serper API key not configured")

        results = await service.search("artificial intelligence", max_results=3)

        assert isinstance(results, list)
        if results:  # May be empty due to rate limits
            assert "title" in results[0]
            assert "url" in results[0]
            assert "snippet" in results[0]
