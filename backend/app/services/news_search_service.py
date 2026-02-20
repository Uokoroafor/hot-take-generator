import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from newsapi import NewsApiClient
from app.core.config import settings
import logging
from app.services.search_quality import (
    SearchQualityConfig,
    apply_recency_window,
    dedupe_records,
    domain_allowed,
    extract_domain,
    score_record,
    tokenize,
)

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
        raw_days = getattr(settings, "search_news_days_default", 14)
        self.default_days = raw_days if isinstance(raw_days, int) else 14
        self._quality = SearchQualityConfig(settings)
        self.allowlist = self._quality.allowlist
        self.blocklist = self._quality.blocklist
        self.trusted_domains = self._quality.trusted_domains
        self.score_weights = self._quality.score_weights

    async def search_recent_news(
        self,
        topic: str,
        max_results: int = 5,
        days_back: int | None = None,
        strict_quality_mode: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search for recent news articles related to the topic using NewsAPI."""
        if not self.newsapi_client:
            logger.warning("NewsAPI client not initialized (missing API key)")
            return []

        effective_days = days_back if days_back is not None else self.default_days

        try:
            # Run the synchronous NewsAPI call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            articles = await loop.run_in_executor(
                None,
                self._fetch_news_api_articles,
                topic,
                max_results,
                effective_days,
                strict_quality_mode,
            )
            return articles
        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return []

    def _fetch_news_api_articles(
        self,
        topic: str,
        max_results: int,
        days_back: int,
        strict_quality_mode: bool,
    ) -> List[Dict[str, Any]]:
        """Fetch articles from NewsAPI (synchronous method)."""
        try:
            from_date = None
            if days_back > 0:
                from_date = (
                    datetime.now(timezone.utc) - timedelta(days=max(1, days_back))
                ).strftime("%Y-%m-%d")
            query = self._build_news_query(topic, strict_quality_mode)
            request_params = {
                "q": query,
                "language": "en",
                "sort_by": "publishedAt",
                "page_size": min(max_results * (3 if strict_quality_mode else 2), 100),
            }
            if from_date:
                request_params["from_param"] = from_date
            response = self.newsapi_client.get_everything(**request_params)

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

            return self._rank_and_filter_articles(
                topic=topic,
                articles=articles,
                max_results=max_results,
                days_back=days_back,
                strict_quality_mode=strict_quality_mode,
            )

        except Exception as e:
            logger.error(f"Error fetching NewsAPI articles: {e}")
            return []

    def _build_news_query(self, topic: str, strict_quality_mode: bool) -> str:
        cleaned = " ".join(topic.split())
        if not cleaned:
            return topic
        if strict_quality_mode and " " in cleaned:
            return f'"{cleaned}" AND (latest OR update OR report)'
        return f"{cleaned} latest"

    def _rank_and_filter_articles(
        self,
        *,
        topic: str,
        articles: List[Dict[str, Any]],
        max_results: int,
        days_back: int,
        strict_quality_mode: bool,
    ) -> List[Dict[str, Any]]:
        topic_tokens = tokenize(topic)
        filtered: List[Dict[str, Any]] = []

        for article in articles:
            title = (article.get("title") or "").strip()
            url = (article.get("url") or "").strip()
            if not title or not url:
                continue

            domain = extract_domain(url)
            if not domain_allowed(domain, self.allowlist, self.blocklist):
                continue
            article["_domain"] = domain

            if strict_quality_mode:
                summary = (article.get("summary") or "").strip()
                overlap = len(topic_tokens & tokenize(f"{title} {summary}"))
                if len(summary) < 90 or overlap == 0:
                    continue
            filtered.append(article)

        deduped = dedupe_records(filtered)
        recent = (
            apply_recency_window(deduped, max(1, days_back))
            if days_back > 0
            else deduped
        )

        for item in recent:
            domain = item.get("_domain") or extract_domain(item.get("url", ""))
            item["_quality_score"] = score_record(
                {**item, "source": domain},
                topic_tokens=topic_tokens,
                topic_text=topic,
                trusted_domains=self.trusted_domains,
                recency_days=max(7, days_back),
                strict_quality_mode=strict_quality_mode,
                **self.score_weights,
            )

        ranked = sorted(
            recent,
            key=lambda r: (r.get("_quality_score", 0.0), bool(r.get("published"))),
            reverse=True,
        )
        final_articles = ranked[:max_results]
        for item in final_articles:
            item.pop("_quality_score", None)
            item.pop("_domain", None)
        return final_articles

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

    async def search_and_format(
        self,
        topic: str,
        max_results: int = 5,
        days_back: int | None = None,
        strict_quality_mode: bool = False,
    ) -> str:
        """Search for news and return formatted context string."""
        articles = await self.search_recent_news(
            topic,
            max_results,
            days_back=days_back,
            strict_quality_mode=strict_quality_mode,
        )
        return self.format_news_context(articles)
