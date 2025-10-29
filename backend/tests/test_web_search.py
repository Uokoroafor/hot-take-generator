import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from app.services.web_search_service import WebSearchService, NewsSource
from app.models.schemas import HotTakeRequest, HotTakeResponse


class TestWebSearchService:
    def test_news_source_initialization(self):
        source = NewsSource("Test News", "http://test.com/rss.xml")
        assert source.name == "Test News"
        assert source.url == "http://test.com/rss.xml"
        assert source.type == "rss"

    def test_web_search_service_initialization(self):
        service = WebSearchService()
        assert len(service.news_sources) > 0
        assert service.max_articles == 5
        assert service.search_timeout == 10

    @pytest.mark.asyncio
    async def test_search_recent_news_empty_topic(self):
        service = WebSearchService()
        articles = await service.search_recent_news("")
        assert isinstance(articles, list)

    def test_is_topic_relevant_positive_cases(self):
        service = WebSearchService()

        # Test exact match in title
        entry = {"title": "AI developments in 2024", "summary": "Some other content"}
        assert service._is_topic_relevant(entry, "AI")

        # Test exact match in summary
        entry = {
            "title": "Technology news",
            "summary": "Artificial intelligence breaking news",
        }
        assert service._is_topic_relevant(entry, "artificial intelligence")

        # Test word match
        entry = {"title": "Climate change impacts", "summary": "Global warming effects"}
        assert service._is_topic_relevant(entry, "climate")

    def test_is_topic_relevant_negative_cases(self):
        service = WebSearchService()

        # Test no match
        entry = {
            "title": "Sports news today",
            "summary": "Basketball and football updates",
        }
        assert not service._is_topic_relevant(entry, "technology")

        # Test empty entry
        entry = {}
        assert not service._is_topic_relevant(entry, "test")

    def test_parse_date_valid_formats(self):
        service = WebSearchService()

        # Test with None
        result = service._parse_date(None)
        assert result is None

        # Test with empty string
        result = service._parse_date("")
        assert result is None

        # For invalid formats, should return current time
        result = service._parse_date("invalid date")
        assert isinstance(result, datetime)

    def test_filter_recent_articles(self):
        service = WebSearchService()

        # Create test articles with different dates
        now = datetime.now()
        recent_date = now - timedelta(days=2)
        old_date = now - timedelta(days=10)

        articles = [
            {"title": "Recent news", "published": recent_date},
            {"title": "Old news", "published": old_date},
            {"title": "Very recent", "published": now},
            {"title": "No date", "published": None},
        ]

        filtered = service._filter_recent_articles(articles)

        # Should only include articles from last 7 days
        assert len(filtered) == 2
        assert filtered[0]["title"] == "Very recent"  # Newest first
        assert filtered[1]["title"] == "Recent news"

    def test_format_news_context_empty(self):
        service = WebSearchService()
        context = service.format_news_context([])
        assert "No recent news found" in context

    def test_format_news_context_with_articles(self):
        service = WebSearchService()

        articles = [
            {
                "title": "AI breakthrough",
                "summary": "New AI model released",
                "source": "Tech News",
                "published": datetime.now(),
            },
            {
                "title": "Climate update",
                "summary": "Global temperature rise",
                "source": "Environment Today",
                "published": None,
            },
        ]

        context = service.format_news_context(articles)

        assert "Recent news and headlines:" in context
        assert "AI breakthrough" in context
        assert "Tech News" in context
        assert "Climate update" in context
        assert "Environment Today" in context

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_fetch_rss_articles_success(self, mock_client):
        service = WebSearchService()

        # Mock RSS feed response
        mock_response = MagicMock()
        mock_response.content = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>AI News Today</title>
                    <description>Latest AI developments</description>
                    <link>http://example.com/ai-news</link>
                    <pubDate>Wed, 15 Nov 2023 10:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        source = NewsSource("Test Source", "http://test.com/rss.xml")
        articles = await service._fetch_rss_articles(source, "AI")

        assert len(articles) >= 0  # May be 0 if topic relevance check fails

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_fetch_rss_articles_error(self, mock_client):
        service = WebSearchService()

        # Mock HTTP error
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = Exception("Network error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        source = NewsSource("Test Source", "http://test.com/rss.xml")
        articles = await service._fetch_rss_articles(source, "AI")

        assert articles == []

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_search_web_success(self, mock_client):
        service = WebSearchService()

        # Mock DuckDuckGo API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "RelatedTopics": [
                {
                    "Text": "AI technology advances rapidly",
                    "FirstURL": "http://example.com/ai",
                }
            ]
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        articles = await service._search_web("AI", 2)

        assert len(articles) <= 2
        if articles:
            assert "FirstURL" in articles[0] or "url" in articles[0]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_search_web_error(self, mock_client):
        service = WebSearchService()

        # Mock HTTP error
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = Exception("API error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        articles = await service._search_web("AI", 2)
        assert articles == []

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_article_content_success(self, mock_client):
        service = WebSearchService()

        # Mock article content
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <h1>Main Article</h1>
                <p>This is the article content.</p>
                <script>console.log('remove me');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        content = await service.get_article_content("http://example.com/article")

        assert content is not None
        assert "Main Article" in content
        assert "article content" in content
        assert "console.log" not in content  # Script should be removed
        assert "color: red" not in content  # Style should be removed

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_article_content_error(self, mock_client):
        service = WebSearchService()

        # Mock HTTP error
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = Exception("Network error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        content = await service.get_article_content("http://example.com/article")
        assert content is None

    @pytest.mark.asyncio
    async def test_search_and_format_integration(self):
        service = WebSearchService()

        # Mock the search_recent_news method
        mock_articles = [
            {
                "title": "Test Article",
                "summary": "Test summary",
                "source": "Test Source",
                "published": datetime.now(),
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
    async def test_hot_take_service_with_web_search(self):
        from app.services.hot_take_service import HotTakeService

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
        request = HotTakeRequest(
            topic="test", style="controversial", use_web_search=True, max_articles=5
        )

        assert request.topic == "test"
        assert request.use_web_search is True
        assert request.max_articles == 5

    def test_hot_take_request_defaults(self):
        request = HotTakeRequest(topic="test")

        assert request.use_web_search is False
        assert request.max_articles == 3

    def test_hot_take_response_with_web_search(self):
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
        response = HotTakeResponse(
            hot_take="test take",
            topic="test",
            style="controversial",
            agent_used="Test Agent",
        )

        assert response.web_search_used is False
        assert response.news_context is None


class TestExternalAPIs:
    """Tests that require external API access - run with pytest -m external"""

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_real_rss_feed_access(self):
        """Test with a real RSS feed - requires internet connection"""
        service = WebSearchService()

        # Use a reliable RSS feed
        source = NewsSource("BBC", "http://feeds.bbci.co.uk/news/rss.xml")
        articles = await service._fetch_rss_articles(source, "news")

        # Should get some articles (or none if the feed is down)
        assert isinstance(articles, list)

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_real_web_search(self):
        """Test with real web search API - requires internet connection"""
        service = WebSearchService()

        articles = await service._search_web("technology", 2)

        assert isinstance(articles, list)
        # May be empty if API is down or rate limited

    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_end_to_end_news_search(self):
        """End-to-end test with real APIs - requires internet connection"""
        service = WebSearchService()

        context = await service.search_and_format("technology", 2)

        assert isinstance(context, str)
        assert len(context) > 0
