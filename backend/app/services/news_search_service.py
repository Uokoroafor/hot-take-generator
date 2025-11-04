import asyncio
from typing import List, Dict, Any
from datetime import datetime
from newsapi import NewsApiClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NewsSearchService:
    """Service for searching news articles using NewsAPI."""

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

            articles = []
            for article in response.get("articles", []):
                try:
                    # Parse the published date
                    published_at = article.get("publishedAt")
                    published_date = None
                    if published_at:
                        try:
                            published_date = datetime.fromisoformat(
                                published_at.replace("Z", "+00:00")
                            )
                        except ValueError:
                            logger.warning(f"Could not parse date: {published_at}")

                    # Use description or content as summary
                    summary = article.get("description", "")
                    if not summary:
                        summary = article.get("content", "")

                    articles.append(
                        {
                            "title": article.get("title", ""),
                            "summary": summary,
                            "url": article.get("url", ""),
                            "published": published_date,
                            "source": article.get("source", {}).get("name", ""),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"Error fetching NewsAPI articles: {e}")
            return []

    def format_news_context(self, articles: List[Dict[str, Any]]) -> str:
        """Format news articles into a context string for the LLM."""
        if not articles:
            return "No recent news found on this topic."

        context_parts = ["Recent news and headlines:"]

        for i, article in enumerate(articles, 1):
            title = article.get("title", "")
            summary = article.get("summary", "")
            source = article.get("source", "")
            url = article.get("url", "")
            published = article.get("published")

            # Truncate summary if too long
            if len(summary) > 200:
                summary = summary[:197] + "..."

            article_text = f"\n{i}. {title}"
            if source:
                article_text += f" ({source})"
            if published:
                article_text += f" - {published.strftime('%Y-%m-%d')}"
            if summary:
                article_text += f"\n   {summary}"
            if url:
                article_text += f"\n   URL: {url}"

            context_parts.append(article_text)

        return "\n".join(context_parts)

    async def search_and_format(self, topic: str, max_results: int = 5) -> str:
        """Search for news and return formatted context string."""
        articles = await self.search_recent_news(topic, max_results)
        return self.format_news_context(articles)
