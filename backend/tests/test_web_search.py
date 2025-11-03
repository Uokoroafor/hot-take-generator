import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.web_search_service import WebSearchService
from app.models.schemas import HotTakeResponse


class TestWebSearchService:
    def test_web_search_service_initialization(self):
        """Test service initializes with proper defaults."""
        service = WebSearchService()
        assert service.max_articles == 5
        assert service.search_timeout == 15

    @patch("app.services.web_search_service.settings")
    def test_newsapi_client_initialization_with_key(self, mock_settings):
        """Test NewsAPI client initializes when API key is present."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = WebSearchService()
        assert service.newsapi_client is not None

    @patch("app.services.web_search_service.settings")
    def test_newsapi_client_initialization_without_key(self, mock_settings):
        """Test NewsAPI client is None when API key is missing."""
        mock_settings.newsapi_api_key = None
        service = WebSearchService()
        assert service.newsapi_client is None

    @pytest.mark.asyncio
    async def test_search_recent_news_no_api_key(self):
        """Test search returns empty list when NewsAPI client is not initialized."""
        with patch("app.services.web_search_service.settings") as mock_settings:
            mock_settings.newsapi_api_key = None
            service = WebSearchService()

            articles = await service.search_recent_news("test topic", max_results=5)
            assert articles == []

    @pytest.mark.asyncio
    @patch("app.services.web_search_service.settings")
    async def test_search_recent_news_success(self, mock_settings):
        """Test successful news search with NewsAPI."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = WebSearchService()

        # Mock NewsAPI response
        mock_newsapi_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "AI breakthrough in 2024",
                    "description": "New AI model released",
                    "url": "https://example.com/article1",
                    "publishedAt": "2024-11-01T10:00:00Z",
                    "source": {"name": "Tech News"},
                },
                {
                    "title": "Machine learning advances",
                    "description": "Latest ML developments",
                    "url": "https://example.com/article2",
                    "publishedAt": "2024-11-01T09:00:00Z",
                    "source": {"name": "AI Today"},
                },
            ],
        }

        # Mock the NewsAPI client
        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_newsapi_response

        articles = await service.search_recent_news("AI", max_results=2)

        assert len(articles) == 2
        assert articles[0]["title"] == "AI breakthrough in 2024"
        assert articles[0]["source"] == "Tech News"
        assert articles[0]["url"] == "https://example.com/article1"
        assert isinstance(articles[0]["published"], datetime)
        assert articles[1]["title"] == "Machine learning advances"

    @pytest.mark.asyncio
    @patch("app.services.web_search_service.settings")
    async def test_search_recent_news_api_error(self, mock_settings):
        """Test error handling when NewsAPI returns an error."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = WebSearchService()

        # Mock NewsAPI to raise an exception
        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.side_effect = Exception("API error")

        articles = await service.search_recent_news("test", max_results=5)
        assert articles == []

    @pytest.mark.asyncio
    @patch("app.services.web_search_service.settings")
    async def test_search_recent_news_bad_status(self, mock_settings):
        """Test handling of bad status from NewsAPI."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = WebSearchService()

        # Mock NewsAPI response with bad status
        mock_newsapi_response = {
            "status": "error",
            "code": "apiKeyInvalid",
            "message": "Invalid API key",
        }

        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_newsapi_response

        articles = await service.search_recent_news("test", max_results=5)
        assert articles == []

    def test_fetch_news_api_articles_success(self):
        """Test _fetch_news_api_articles with successful response."""
        service = WebSearchService()

        mock_newsapi_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "Climate change update",
                    "description": "Latest climate news",
                    "content": "Full article content here...",
                    "url": "https://example.com/climate",
                    "publishedAt": "2024-11-01T12:00:00Z",
                    "source": {"name": "Environment News"},
                }
            ],
        }

        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_newsapi_response

        articles = service._fetch_news_api_articles("climate change", max_results=1)

        assert len(articles) == 1
        assert articles[0]["title"] == "Climate change update"
        assert articles[0]["source"] == "Environment News"
        assert articles[0]["summary"] == "Latest climate news"

    def test_fetch_news_api_articles_with_content_fallback(self):
        """Test that content is used as summary when description is missing."""
        service = WebSearchService()

        mock_newsapi_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article",
                    "description": "",  # Empty description
                    "content": "This is the article content",
                    "url": "https://example.com/test",
                    "publishedAt": "2024-11-01T12:00:00Z",
                    "source": {"name": "Test Source"},
                }
            ],
        }

        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_newsapi_response

        articles = service._fetch_news_api_articles("test", max_results=1)

        assert articles[0]["summary"] == "This is the article content"

    def test_fetch_news_api_articles_date_parsing(self):
        """Test proper date parsing from NewsAPI response."""
        service = WebSearchService()

        mock_newsapi_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article",
                    "description": "Test description",
                    "url": "https://example.com/test",
                    "publishedAt": "2024-11-01T15:30:45Z",
                    "source": {"name": "Test Source"},
                }
            ],
        }

        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_newsapi_response

        articles = service._fetch_news_api_articles("test", max_results=1)

        assert isinstance(articles[0]["published"], datetime)
        assert articles[0]["published"].year == 2024
        assert articles[0]["published"].month == 11
        assert articles[0]["published"].day == 1

    def test_fetch_news_api_articles_invalid_date(self):
        """Test handling of invalid date format."""
        service = WebSearchService()

        mock_newsapi_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article",
                    "description": "Test description",
                    "url": "https://example.com/test",
                    "publishedAt": "invalid-date-format",
                    "source": {"name": "Test Source"},
                }
            ],
        }

        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_newsapi_response

        articles = service._fetch_news_api_articles("test", max_results=1)

        assert articles[0]["published"] is None

    def test_format_news_context_empty(self):
        """Test formatting with no articles."""
        service = WebSearchService()
        context = service.format_news_context([])
        assert "No recent news found" in context

    def test_format_news_context_with_articles(self):
        """Test formatting with multiple articles."""
        service = WebSearchService()

        articles = [
            {
                "title": "AI breakthrough",
                "summary": "New AI model released",
                "source": "Tech News",
                "url": "https://example.com/ai",
                "published": datetime.now(timezone.utc),
            },
            {
                "title": "Climate update",
                "summary": "Global temperature rise",
                "source": "Environment Today",
                "url": "https://example.com/climate",
                "published": None,
            },
        ]

        context = service.format_news_context(articles)

        assert "Recent news and headlines:" in context
        assert "AI breakthrough" in context
        assert "Tech News" in context
        assert "Climate update" in context
        assert "Environment Today" in context
        assert "https://example.com/ai" in context

    def test_format_news_context_truncates_summary(self):
        """Test that long summaries are truncated."""
        service = WebSearchService()

        long_summary = "A" * 300  # Summary longer than 200 chars
        articles = [
            {
                "title": "Test Article",
                "summary": long_summary,
                "source": "Test Source",
                "url": "https://example.com/test",
                "published": datetime.now(timezone.utc),
            }
        ]

        context = service.format_news_context(articles)

        # Should contain truncated version with "..."
        assert "..." in context
        assert long_summary not in context

    @pytest.mark.asyncio
    @patch("app.services.web_search_service.settings")
    async def test_search_and_format_integration(self, mock_settings):
        """Test search_and_format integration."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = WebSearchService()

        mock_articles = [
            {
                "title": "Test Article",
                "summary": "Test summary",
                "source": "Test Source",
                "url": "https://example.com/test",
                "published": datetime.now(timezone.utc),
            }
        ]

        with patch.object(service, "search_recent_news", return_value=mock_articles):
            result = await service.search_and_format("test topic", 1)

            assert "Recent news and headlines:" in result
            assert "Test Article" in result
            assert "Test Source" in result


class TestWebSearchIntegration:
    """Test web search integration with the hot take service"""

    @pytest.mark.asyncio
    @patch("app.services.web_search_service.settings")
    async def test_hot_take_service_with_web_search(self, mock_settings):
        """Test hot take service with web search enabled."""
        from app.services.hot_take_service import HotTakeService

        mock_settings.newsapi_api_key = "test_api_key"
        service = HotTakeService()

        # Mock the web search
        mock_context = "Recent news: AI technology advances"
        with patch.object(
            service.web_search_service, "search_and_format", return_value=mock_context
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
                    use_web_search=True,
                    max_articles=2,
                )

                assert isinstance(result, HotTakeResponse)
                assert result.web_search_used is True
                assert result.news_context == mock_context

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
                topic="AI", style="controversial", use_web_search=False
            )

            assert isinstance(result, HotTakeResponse)
            assert result.web_search_used is False
            assert result.news_context is None

    @pytest.mark.asyncio
    async def test_hot_take_service_web_search_error(self):
        """Test hot take service continues when web search fails."""
        from app.services.hot_take_service import HotTakeService

        service = HotTakeService()

        # Mock web search to raise an error
        with patch.object(
            service.web_search_service,
            "search_and_format",
            side_effect=Exception("Search failed"),
        ):
            # Mock the agent response
            with patch.object(
                service.agents["openai"],
                "generate_hot_take",
                return_value="AI hot take",
            ):
                result = await service.generate_hot_take(
                    topic="AI", style="controversial", use_web_search=True
                )

                # Should continue without web search when it fails
                assert isinstance(result, HotTakeResponse)
                assert result.web_search_used is False


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
        assert request.max_articles == 3

    def test_hot_take_response_with_web_search(self):
        """Test HotTakeResponse with web search data."""
        response = HotTakeResponse(
            hot_take="test take",
            topic="test",
            style="controversial",
            agent_used="Test Agent",
            web_search_used=True,
            news_context="Test news context",
        )

        assert response.web_search_used is True
        assert response.news_context == "Test news context"

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


class TestNewsAPIExternalIntegration:
    """Tests that require external NewsAPI access - run with pytest -m external"""

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_real_newsapi_search(self):
        """Test with real NewsAPI - requires API key and internet connection."""
        service = WebSearchService()

        if not service.newsapi_client:
            pytest.skip("NewsAPI key not configured")

        articles = await service.search_recent_news("technology", max_results=3)

        assert isinstance(articles, list)
        if articles:  # May be empty due to rate limits
            assert "title" in articles[0]
            assert "source" in articles[0]
            assert "url" in articles[0]

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_end_to_end_news_search(self):
        """End-to-end test with real NewsAPI - requires API key and internet."""
        service = WebSearchService()

        if not service.newsapi_client:
            pytest.skip("NewsAPI key not configured")

        context = await service.search_and_format("artificial intelligence", 2)

        assert isinstance(context, str)
        assert len(context) > 0
        # Should either have news or the "no news found" message
        assert "Recent news" in context or "No recent news found" in context
