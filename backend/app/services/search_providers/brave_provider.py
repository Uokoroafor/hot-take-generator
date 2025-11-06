import httpx
import logging
from typing import List, Dict, Any
from .base import SearchProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class BraveSearchProvider(SearchProvider):
    """Brave Search API provider for web search."""

    def __init__(self):
        self.api_key = settings.brave_api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.timeout = 15

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Brave Search API."""
        if not self.is_configured():
            logger.warning("Brave Search API key not configured")
            return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key,
                }

                params = {
                    "q": query,
                    "count": min(max_results, 20),  # Brave max is 20 for free tier
                }

                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout,
                )

                response.raise_for_status()
                data = response.json()

                return self._parse_results(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Brave Search API HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Brave Search API error: {e}")
            return []

    def _parse_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Brave Search API response into standardized format."""
        results = []

        web_results = data.get("web", {}).get("results", [])

        for item in web_results:
            try:
                # Parse age field if available (e.g., "2 days ago")
                published = None
                if "age" in item and item["age"]:
                    # For now, we'll set published to None
                    # Brave doesn't always provide exact dates
                    published = None

                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "published": published,
                        "source": self._extract_domain(item.get("url", "")),
                    }
                )
            except Exception as e:
                logger.warning(f"Error parsing Brave search result: {e}")
                continue

        return results

    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove 'www.' prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def is_configured(self) -> bool:
        """Check if Brave API key is configured."""
        return bool(self.api_key)

    @property
    def name(self) -> str:
        """Return provider name."""
        return "brave"
