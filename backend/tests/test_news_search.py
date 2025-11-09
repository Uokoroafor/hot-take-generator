import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.news_search_service import NewsSearchService


class TestNewsSearchService:
    """Tests for news search service using NewsAPI."""

    def test_news_search_service_initialization(self):
        """Test service initializes with proper defaults."""
        service = NewsSearchService()
        assert service.max_articles == 5
        assert service.search_timeout == 15

    @patch("app.services.news_search_service.settings")
    def test_newsapi_client_initialization_with_key(self, mock_settings):
        """Test NewsAPI client initializes when API key is present."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = NewsSearchService()
        assert service.newsapi_client is not None

    @patch("app.services.news_search_service.settings")
    def test_newsapi_client_initialization_without_key(self, mock_settings):
        """Test NewsAPI client is None when API key is missing."""
        mock_settings.newsapi_api_key = None
        service = NewsSearchService()
        assert service.newsapi_client is None

    @pytest.mark.asyncio
    async def test_search_recent_news_no_api_key(self):
        """Test search returns empty list when NewsAPI client is not initialized."""
        with patch("app.services.news_search_service.settings") as mock_settings:
            mock_settings.newsapi_api_key = None
            service = NewsSearchService()

            articles = await service.search_recent_news("test topic", max_results=5)
            assert articles == []

    @pytest.mark.asyncio
    @patch("app.services.news_search_service.settings")
    async def test_search_recent_news_success(self, mock_settings):
        """Test successful news search with NewsAPI."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = NewsSearchService()

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
    @patch("app.services.news_search_service.settings")
    async def test_search_recent_news_api_error(self, mock_settings):
        """Test error handling when NewsAPI returns an error."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = NewsSearchService()

        # Mock NewsAPI to raise an exception
        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.side_effect = Exception("API error")

        articles = await service.search_recent_news("test", max_results=5)
        assert articles == []

    @pytest.mark.asyncio
    @patch("app.services.news_search_service.settings")
    async def test_search_recent_news_bad_status(self, mock_settings):
        """Test handling of bad status from NewsAPI."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = NewsSearchService()

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

    def test_format_news_context_empty(self):
        """Test formatting with no articles."""
        service = NewsSearchService()
        context = service.format_news_context([])
        assert "No recent news found" in context

    def test_format_news_context_with_articles(self):
        """Test formatting with multiple articles."""
        service = NewsSearchService()

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
        service = NewsSearchService()

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
    @patch("app.services.news_search_service.settings")
    async def test_search_and_format_integration(self, mock_settings):
        """Test search_and_format integration."""
        mock_settings.newsapi_api_key = "test_api_key"
        service = NewsSearchService()

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
