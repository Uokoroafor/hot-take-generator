import asyncio
import httpx
import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import quote
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class NewsSource:
    def __init__(self, name: str, url: str, type: str = "rss"):
        self.name = name
        self.url = url
        self.type = type

class WebSearchService:
    def __init__(self):
        self.news_sources = [
            NewsSource("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
            NewsSource("Reuters", "http://feeds.reuters.com/reuters/topNews"),
            NewsSource("AP News", "https://rsshub.app/ap/topics/apf-topnews"),
            NewsSource("CNN", "http://rss.cnn.com/rss/edition.rss"),
            NewsSource("NPR", "https://feeds.npr.org/1001/rss.xml"),
        ]
        self.max_articles = 5
        self.search_timeout = 10

    async def search_recent_news(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for recent news articles related to the topic"""
        articles = []

        # Try RSS feeds first
        rss_articles = await self._search_rss_feeds(topic, max_results)
        articles.extend(rss_articles)

        # If we don't have enough articles, try web search
        if len(articles) < max_results:
            web_articles = await self._search_web(topic, max_results - len(articles))
            articles.extend(web_articles)

        return articles[:max_results]

    async def _search_rss_feeds(self, topic: str, max_results: int) -> List[Dict[str, Any]]:
        """Search RSS feeds for topic-related articles"""
        articles = []

        for source in self.news_sources:
            try:
                source_articles = await self._fetch_rss_articles(source, topic)
                articles.extend(source_articles)

                if len(articles) >= max_results:
                    break

            except Exception as e:
                logger.warning(f"Failed to fetch from {source.name}: {str(e)}")
                continue

        # Sort by publication date (newest first) and filter recent articles
        articles = self._filter_recent_articles(articles)
        return articles[:max_results]

    async def _fetch_rss_articles(self, source: NewsSource, topic: str) -> List[Dict[str, Any]]:
        """Fetch articles from an RSS feed"""
        try:
            async with httpx.AsyncClient(timeout=self.search_timeout) as client:
                response = await client.get(source.url)
                response.raise_for_status()

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:10]:  # Limit to 10 entries per source
                if self._is_topic_relevant(entry, topic):
                    article = {
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "published": self._parse_date(entry.get("published")),
                        "source": source.name
                    }
                    articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS from {source.name}: {str(e)}")
            return []

    async def _search_web(self, topic: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback web search using DuckDuckGo Instant Answer API"""
        articles = []

        try:
            # Use DuckDuckGo's instant answer API for news search
            search_query = f"{topic} news"
            url = f"https://api.duckduckgo.com/?q={quote(search_query)}&format=json&no_html=1&skip_disambig=1"

            async with httpx.AsyncClient(timeout=self.search_timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                # Extract relevant results
                if "RelatedTopics" in data:
                    for item in data["RelatedTopics"][:max_results]:
                        if isinstance(item, dict) and "Text" in item:
                            article = {
                                "title": item.get("Text", "")[:100] + "...",
                                "summary": item.get("Text", ""),
                                "url": item.get("FirstURL", ""),
                                "published": datetime.now(),
                                "source": "DuckDuckGo"
                            }
                            articles.append(article)

        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")

        return articles

    def _is_topic_relevant(self, entry: Dict[str, Any], topic: str) -> bool:
        """Check if an RSS entry is relevant to the topic"""
        topic_lower = topic.lower()

        # Check title and summary for topic relevance
        title = entry.get("title", "").lower()
        summary = entry.get("summary", "").lower()

        return (topic_lower in title or
                topic_lower in summary or
                any(word in title for word in topic_lower.split()) or
                any(word in summary for word in topic_lower.split()))

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse various date formats from RSS feeds"""
        if not date_str:
            return None

        try:
            # Try parsing with feedparser's built-in parser
            import time
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime(*parsed_time[:6])
        except:
            pass

        # Fallback to current time
        return datetime.now()

    def _filter_recent_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles to only include recent ones (last 7 days)"""
        cutoff_date = datetime.now() - timedelta(days=7)

        recent_articles = []
        for article in articles:
            pub_date = article.get("published")
            if pub_date and pub_date > cutoff_date:
                recent_articles.append(article)

        # Sort by publication date (newest first)
        recent_articles.sort(key=lambda x: x.get("published", datetime.min), reverse=True)

        return recent_articles

    async def get_article_content(self, url: str) -> Optional[str]:
        """Extract full article content from URL"""
        try:
            async with httpx.AsyncClient(timeout=self.search_timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit content length
            return text[:2000] if text else None

        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {str(e)}")
            return None

    def format_news_context(self, articles: List[Dict[str, Any]]) -> str:
        """Format news articles into context for AI agents"""
        if not articles:
            return "No recent news found for this topic."

        context = "Recent news and headlines:\n\n"

        for i, article in enumerate(articles, 1):
            context += f"{i}. {article['title']}\n"
            if article.get('summary'):
                context += f"   Summary: {article['summary'][:200]}...\n"
            context += f"   Source: {article['source']}\n"
            if article.get('published'):
                context += f"   Published: {article['published'].strftime('%Y-%m-%d')}\n"
            context += "\n"

        return context

    async def search_and_format(self, topic: str, max_results: int = 3) -> str:
        """Search for news and return formatted context"""
        articles = await self.search_recent_news(topic, max_results)
        return self.format_news_context(articles)