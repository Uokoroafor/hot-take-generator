from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SearchProvider(ABC):
    """Abstract base class for search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for web content based on the query.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            List of search results with standardized format:
            [
                {
                    "title": str,
                    "url": str,
                    "snippet": str,
                    "published": datetime or None,
                    "source": str or None,
                }
            ]
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured with necessary API keys."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the search provider."""
        pass
