import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from app.services.search_providers.brave_provider import BraveSearchProvider
from app.services.search_providers.serper_provider import SerperSearchProvider


class TestBraveSearchProvider:
    """Tests for Brave Search API provider."""

    @patch("app.services.search_providers.brave_provider.settings")
    def test_brave_provider_initialization_with_key(self, mock_settings):
        """Test Brave provider initializes with API key."""
        mock_settings.brave_api_key = "test_brave_key"
        provider = BraveSearchProvider()
        assert provider.is_configured() is True
        assert provider.name == "brave"

    @patch("app.services.search_providers.brave_provider.settings")
    def test_brave_provider_initialization_without_key(self, mock_settings):
        """Test Brave provider without API key."""
        mock_settings.brave_api_key = None
        provider = BraveSearchProvider()
        assert provider.is_configured() is False

    @pytest.mark.asyncio
    @patch("app.services.search_providers.brave_provider.settings")
    async def test_brave_search_no_api_key(self, mock_settings):
        """Test Brave search returns empty list when not configured."""
        mock_settings.brave_api_key = None
        provider = BraveSearchProvider()

        results = await provider.search("test query", max_results=5)
        assert results == []

    @pytest.mark.asyncio
    @patch("app.services.search_providers.brave_provider.settings")
    @patch("httpx.AsyncClient")
    async def test_brave_search_success(self, mock_client_class, mock_settings):
        """Test successful Brave search."""
        mock_settings.brave_api_key = "test_brave_key"
        provider = BraveSearchProvider()

        # Mock HTTP response
        mock_response_data = {
            "web": {
                "results": [
                    {
                        "title": "Test Result 1",
                        "url": "https://example.com/page1",
                        "description": "Test description 1",
                        "age": "2 days ago",
                    },
                    {
                        "title": "Test Result 2",
                        "url": "https://test.com/page2",
                        "description": "Test description 2",
                    },
                ]
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        results = await provider.search("test query", max_results=5)

        assert len(results) == 2
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["url"] == "https://example.com/page1"
        assert results[0]["snippet"] == "Test description 1"
        assert results[0]["source"] == "example.com"
        assert results[1]["source"] == "test.com"

    @pytest.mark.asyncio
    @patch("app.services.search_providers.brave_provider.settings")
    async def test_brave_search_http_error(self, mock_settings):
        """Test Brave search handles HTTP errors."""
        mock_settings.brave_api_key = "test_brave_key"
        provider = BraveSearchProvider()

        # Mock httpx to raise an HTTPStatusError
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=mock_response
            )

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            results = await provider.search("test query", max_results=5)
            assert results == []


class TestSerperSearchProvider:
    """Tests for Serper API provider."""

    @patch("app.services.search_providers.serper_provider.settings")
    def test_serper_provider_initialization_with_key(self, mock_settings):
        """Test Serper provider initializes with API key."""
        mock_settings.serper_api_key = "test_serper_key"
        provider = SerperSearchProvider()
        assert provider.is_configured() is True
        assert provider.name == "serper"

    @patch("app.services.search_providers.serper_provider.settings")
    def test_serper_provider_initialization_without_key(self, mock_settings):
        """Test Serper provider without API key."""
        mock_settings.serper_api_key = None
        provider = SerperSearchProvider()
        assert provider.is_configured() is False

    @pytest.mark.asyncio
    @patch("app.services.search_providers.serper_provider.settings")
    async def test_serper_search_no_api_key(self, mock_settings):
        """Test Serper search returns empty list when not configured."""
        mock_settings.serper_api_key = None
        provider = SerperSearchProvider()

        results = await provider.search("test query", max_results=5)
        assert results == []

    @pytest.mark.asyncio
    @patch("app.services.search_providers.serper_provider.settings")
    @patch("httpx.AsyncClient")
    async def test_serper_search_success(self, mock_client_class, mock_settings):
        """Test successful Serper search."""
        mock_settings.serper_api_key = "test_serper_key"
        provider = SerperSearchProvider()

        # Mock HTTP response
        mock_response_data = {
            "organic": [
                {
                    "title": "Serper Result 1",
                    "link": "https://example.com/article1",
                    "snippet": "Serper test snippet 1",
                },
                {
                    "title": "Serper Result 2",
                    "link": "https://test.org/article2",
                    "snippet": "Serper test snippet 2",
                },
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        results = await provider.search("test query", max_results=5)

        assert len(results) == 2
        assert results[0]["title"] == "Serper Result 1"
        assert results[0]["url"] == "https://example.com/article1"
        assert results[0]["snippet"] == "Serper test snippet 1"
        assert results[0]["source"] == "example.com"
        assert results[1]["source"] == "test.org"

    @pytest.mark.asyncio
    @patch("app.services.search_providers.serper_provider.settings")
    async def test_serper_search_http_error(self, mock_settings):
        """Test Serper search handles HTTP errors."""
        mock_settings.serper_api_key = "test_serper_key"
        provider = SerperSearchProvider()

        # Mock httpx to raise an HTTPStatusError
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Forbidden", request=MagicMock(), response=mock_response
            )

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            results = await provider.search("test query", max_results=5)
            assert results == []
