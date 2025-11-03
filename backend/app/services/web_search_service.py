import asyncio
from typing import List, Dict, Any
from datetime import datetime, timezone
from newsapi import NewsApiClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class WebSearchService:
    def __init__(self):
        # Initialize NewsAPI client with API key from settings
        self.newsapi_client = (
            NewsApiClient(api_key=settings.newsapi_api_key)
            if settings.newsapi_api_key
            else None
        )
        self.max_articles = 5
        self.search_timeout = 15

    async def search_recent_news(
        self, topic: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for recent news articles related to the topic using NewsAPI."""
        if not self.newsapi_client:
            logger.warning("NewsAPI client not initialized (missing API key)")
            return []

        try:
            # Run the synchronous NewsAPI call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            articles = await loop.run_in_executor(
                None, self._fetch_news_api_articles, topic, max_results
            )
            return articles
        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return []

    def _fetch_news_api_articles(
        self, topic: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Fetch articles from NewsAPI (synchronous method)."""
        try:
            # Use everything endpoint for broader search
            # Sort by publishedAt (most recent first)
            response = self.newsapi_client.get_everything(
                q=topic,
                language="en",
                sort_by="publishedAt",
                page_size=min(max_results, 100),  # NewsAPI max is 100
            )

            if response.get("status") != "ok":
                logger.error(f"NewsAPI returned status: {response.get('status')}")
                return []

            articles_data = response.get("articles", [])
            formatted_articles = []

            for article in articles_data[:max_results]:
                # Parse the published date
                published_str = article.get("publishedAt")
                published_dt = None
                if published_str:
                    try:
                        # NewsAPI returns ISO 8601 format
                        published_dt = datetime.fromisoformat(
                            published_str.replace("Z", "+00:00")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse date {published_str}: {e}")

                formatted_articles.append(
                    {
                        "title": article.get("title", ""),
                        "summary": article.get("description", "")
                        or article.get("content", ""),
                        "url": article.get("url", ""),
                        "published": published_dt,
                        "source": article.get("source", {}).get("name", "Unknown"),
                    }
                )

            return formatted_articles

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return []

    def format_news_context(self, articles: List[Dict[str, Any]]) -> str:
        """Format news articles into context for AI agents."""
        if not articles:
            return "No recent news found for this topic."

        lines = ["Recent news and headlines:", ""]
        for i, a in enumerate(articles, 1):
            lines.append(f"{i}. {a.get('title', '')}")
            if a.get("summary"):
                lines.append(f"   Summary: {a['summary'][:200]}...")
            lines.append(f"   Source: {a.get('source', '')}")
            if a.get("published"):
                lines.append(
                    f"   Published: {a['published'].astimezone(timezone.utc).strftime('%Y-%m-%d')}"
                )
            if a.get("url"):
                lines.append(f"   URL: {a['url']}")
            lines.append("")
        return "\n".join(lines)

    async def search_and_format(self, topic: str, max_results: int = 3) -> str:
        articles = await self.search_recent_news(topic, max_results)
        return self.format_news_context(articles)
