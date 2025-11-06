import httpx
import logging
from typing import List, Dict, Any
from .base import SearchProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class SerperSearchProvider(SearchProvider):
    """Serper.dev API provider for web search."""

    def __init__(self):
        self.api_key = settings.serper_api_key
        self.base_url = "https://google.serper.dev/search"
        self.timeout = 15

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Serper API."""
        if not self.is_configured():
            logger.warning("Serper API key not configured")
            return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json",
                }

                payload = {
                    "q": query,
                    "num": min(max_results, 10),  # Serper typically supports up to 10
                }

                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )

                response.raise_for_status()
                data = response.json()

                return self._parse_results(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Serper API HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Serper API error: {e}")
            return []

    def _parse_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Serper API response into standardized format."""
        results = []

        organic_results = data.get("organic", [])

        for item in organic_results:
            try:
                # Serper doesn't provide publish dates by default
                published = None

                # Extract date if available in snippet
                date_str = item.get("date")
                if date_str:
                    try:
                        # Serper sometimes includes dates, parse if possible
                        # Format varies, so we'll leave as None for now
                        published = None
                    except Exception:
                        published = None

                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "published": published,
                        "source": self._extract_domain(item.get("link", "")),
                    }
                )
            except Exception as e:
                logger.warning(f"Error parsing Serper search result: {e}")
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
        """Check if Serper API key is configured."""
        return bool(self.api_key)

    @property
    def name(self) -> str:
        """Return provider name."""
        return "serper"
