from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.services.search_providers import (
    SearchProvider,
    BraveSearchProvider,
    SerperSearchProvider,
)
from app.services.search_quality import (
    SearchQualityConfig,
    dedupe_records,
    domain_allowed,
    extract_domain,
    score_record,
    tokenize,
)

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for web search using configurable search providers."""

    def __init__(self, provider_name: Optional[str] = None):
        """
        Initialize web search service with a specific provider.

        Args:
            provider_name: Name of the provider to use ('brave', 'serper').
                          If None, uses the first configured provider.
        """
        self.providers = {
            "brave": BraveSearchProvider(),
            "serper": SerperSearchProvider(),
        }

        # Select provider
        if provider_name:
            if provider_name not in self.providers:
                logger.warning(
                    f"Provider '{provider_name}' not found. Available: {list(self.providers.keys())}"
                )
                self.provider = None
            else:
                self.provider = self.providers[provider_name]
        else:
            # Auto-select first configured provider
            self.provider = self._get_first_configured_provider()

        if self.provider:
            logger.info(f"Using search provider: {self.provider.name}")
        else:
            logger.warning("No search provider configured")

        self._quality = SearchQualityConfig(settings)
        self.allowlist = self._quality.allowlist
        self.blocklist = self._quality.blocklist
        self.trusted_domains = self._quality.trusted_domains
        self.score_weights = self._quality.score_weights

    def _get_first_configured_provider(self) -> Optional[SearchProvider]:
        """Get the first configured provider."""
        for provider in self.providers.values():
            if provider.is_configured():
                return provider
        return None

    async def search(
        self,
        query: str,
        max_results: int = 5,
        strict_quality_mode: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search the web for the given query.

        Returns:
            List of search results with format:
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
        if not self.provider:
            logger.warning("No search provider available")
            return []

        if not self.provider.is_configured():
            logger.warning(f"Provider {self.provider.name} is not configured")
            return []

        try:
            fetch_count = min(20, max_results * (3 if strict_quality_mode else 2))
            results = await self.provider.search(query, fetch_count)
            return self._rank_and_filter_results(
                query=query,
                results=results,
                max_results=max_results,
                strict_quality_mode=strict_quality_mode,
            )
        except Exception as e:
            logger.error(f"Search failed with provider {self.provider.name}: {e}")
            return []

    def _rank_and_filter_results(
        self,
        *,
        query: str,
        results: List[Dict[str, Any]],
        max_results: int,
        strict_quality_mode: bool,
    ) -> List[Dict[str, Any]]:
        topic_tokens = tokenize(query)
        filtered: List[Dict[str, Any]] = []

        for result in results:
            title = (result.get("title") or "").strip()
            url = (result.get("url") or "").strip()
            if not title or not url:
                continue

            domain = extract_domain(result.get("source") or url)
            if not domain_allowed(domain, self.allowlist, self.blocklist):
                continue
            result["source"] = domain

            if strict_quality_mode:
                snippet = (result.get("snippet") or "").strip()
                overlap = len(topic_tokens & tokenize(f"{title} {snippet}"))
                if len(snippet) < 80 or overlap == 0:
                    continue

            filtered.append(result)

        deduped = dedupe_records(filtered)
        for item in deduped:
            item["_quality_score"] = score_record(
                item,
                topic_tokens=topic_tokens,
                topic_text=query,
                trusted_domains=self.trusted_domains,
                recency_days=30,
                strict_quality_mode=strict_quality_mode,
                **self.score_weights,
            )

        ranked = sorted(
            deduped,
            key=lambda r: (r.get("_quality_score", 0.0), bool(r.get("published"))),
            reverse=True,
        )
        final_results = ranked[:max_results]
        for item in final_results:
            item.pop("_quality_score", None)
        return final_results

    def format_search_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into a context string for the LLM."""
        if not results:
            return "No web search results found for this topic."

        context_parts = ["Web search results:"]

        for i, result in enumerate(results, 1):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            source = result.get("source", "")
            url = result.get("url", "")
            published = result.get("published")

            # Truncate snippet if too long
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."

            result_text = f"\n{i}. {title}"
            if source:
                result_text += f" ({source})"
            if published:
                result_text += f" - {published.strftime('%Y-%m-%d')}"
            if snippet:
                result_text += f"\n   {snippet}"
            if url:
                result_text += f"\n   URL: {url}"

            context_parts.append(result_text)

        return "\n".join(context_parts)

    async def search_and_format(
        self, query: str, max_results: int = 5, strict_quality_mode: bool = False
    ) -> str:
        """Search the web and return formatted context string."""
        results = await self.search(query, max_results, strict_quality_mode)
        return self.format_search_context(results)

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())

    def get_configured_providers(self) -> List[str]:
        """Get list of configured provider names."""
        return [
            name
            for name, provider in self.providers.items()
            if provider.is_configured()
        ]
