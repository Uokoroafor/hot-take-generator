import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
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
        mock_settings.search_news_days_default = 14
        mock_settings.search_domain_allowlist = ""
        mock_settings.search_domain_blocklist = ""
        mock_settings.search_trusted_domains = ""
        mock_settings.search_score_weight_relevance = 0.60
        mock_settings.search_score_weight_recency = 0.20
        mock_settings.search_score_weight_snippet = 0.10
        mock_settings.search_score_weight_domain = 0.10
        mock_settings.search_score_strict_no_overlap_penalty = 0.35
        service = NewsSearchService()

        # Mock NewsAPI response with recent dates
        recent_date_1 = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        recent_date_2 = (datetime.now(timezone.utc) - timedelta(days=2)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        mock_newsapi_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "AI breakthrough in 2024",
                    "description": "New AI model released",
                    "url": "https://example.com/article1",
                    "publishedAt": recent_date_1,
                    "source": {"name": "Tech News"},
                },
                {
                    "title": "Machine learning advances",
                    "description": "Latest ML developments",
                    "url": "https://example.com/article2",
                    "publishedAt": recent_date_2,
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
    async def test_search_recent_news_uses_default_days(self, mock_settings):
        """Test that default_days is used when days_back is not provided."""
        mock_settings.newsapi_api_key = "test_api_key"
        mock_settings.search_news_days_default = 14
        mock_settings.search_domain_allowlist = ""
        mock_settings.search_domain_blocklist = ""
        mock_settings.search_trusted_domains = "reuters.com"
        mock_settings.search_score_weight_relevance = 0.60
        mock_settings.search_score_weight_recency = 0.20
        mock_settings.search_score_weight_snippet = 0.10
        mock_settings.search_score_weight_domain = 0.10
        mock_settings.search_score_strict_no_overlap_penalty = 0.35
        service = NewsSearchService()

        mock_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "AI news",
                    "description": "Artificial intelligence update",
                    "url": "https://example.com/ai",
                    "publishedAt": "2024-11-01T10:00:00Z",
                    "source": {"name": "Tech News"},
                },
            ],
        }

        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_response

        await service.search_recent_news("AI", max_results=5)

        call_kwargs = service.newsapi_client.get_everything.call_args
        # Should have from_param set because default_days (14) > 0
        assert "from_param" in (
            call_kwargs.kwargs if call_kwargs.kwargs else {}
        ) or any("from_param" in str(arg) for arg in call_kwargs)

    @pytest.mark.asyncio
    @patch("app.services.news_search_service.settings")
    async def test_search_recent_news_with_explicit_days_back(self, mock_settings):
        """Test search with explicit days_back parameter."""
        mock_settings.newsapi_api_key = "test_api_key"
        mock_settings.search_news_days_default = 14
        mock_settings.search_domain_allowlist = ""
        mock_settings.search_domain_blocklist = ""
        mock_settings.search_trusted_domains = ""
        mock_settings.search_score_weight_relevance = 0.60
        mock_settings.search_score_weight_recency = 0.20
        mock_settings.search_score_weight_snippet = 0.10
        mock_settings.search_score_weight_domain = 0.10
        mock_settings.search_score_strict_no_overlap_penalty = 0.35
        service = NewsSearchService()

        mock_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "AI breakthrough",
                    "description": "Artificial intelligence research update",
                    "url": "https://example.com/ai",
                    "publishedAt": "2024-11-01T10:00:00Z",
                    "source": {"name": "Tech News"},
                },
            ],
        }
        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_response

        articles = await service.search_recent_news("AI", max_results=5, days_back=7)
        assert isinstance(articles, list)

    @pytest.mark.asyncio
    @patch("app.services.news_search_service.settings")
    async def test_search_with_strict_quality_mode(self, mock_settings):
        """Test strict quality mode fetches more and filters harder."""
        mock_settings.newsapi_api_key = "test_api_key"
        mock_settings.search_news_days_default = 14
        mock_settings.search_domain_allowlist = ""
        mock_settings.search_domain_blocklist = ""
        mock_settings.search_trusted_domains = ""
        mock_settings.search_score_weight_relevance = 0.60
        mock_settings.search_score_weight_recency = 0.20
        mock_settings.search_score_weight_snippet = 0.10
        mock_settings.search_score_weight_domain = 0.10
        mock_settings.search_score_strict_no_overlap_penalty = 0.35
        service = NewsSearchService()

        mock_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "AI breakthrough in artificial intelligence",
                    "description": "A " * 50 + "artificial intelligence research",
                    "url": "https://example.com/ai-good",
                    "publishedAt": "2024-11-01T10:00:00Z",
                    "source": {"name": "Tech News"},
                },
                {
                    "title": "Unrelated cooking article",
                    "description": "Short",
                    "url": "https://example.com/cooking",
                    "publishedAt": "2024-11-01T09:00:00Z",
                    "source": {"name": "Food Blog"},
                },
            ],
        }
        service.newsapi_client = MagicMock()
        service.newsapi_client.get_everything.return_value = mock_response

        articles = await service.search_recent_news(
            "artificial intelligence",
            max_results=5,
            days_back=14,
            strict_quality_mode=True,
        )

        # The short unrelated article should be filtered out in strict mode
        titles = [a["title"] for a in articles]
        assert "Unrelated cooking article" not in titles

    def test_build_news_query_normal(self):
        """Test query building in normal mode."""
        service = NewsSearchService()
        query = service._build_news_query("artificial intelligence", False)
        assert "artificial intelligence" in query
        assert "latest" in query

    def test_build_news_query_strict(self):
        """Test query building in strict mode."""
        service = NewsSearchService()
        query = service._build_news_query("artificial intelligence", True)
        assert '"artificial intelligence"' in query
        assert "AND" in query

    def test_build_news_query_single_word_strict(self):
        """Test query building with single word in strict mode."""
        service = NewsSearchService()
        query = service._build_news_query("AI", True)
        # Single word shouldn't get exact phrase wrapping
        assert "AND" not in query

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
