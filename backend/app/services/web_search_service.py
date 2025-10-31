import asyncio
import httpx
import feedparser
from typing import List, Dict, Any, Optional, Iterable
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
import logging
import re

logger = logging.getLogger(__name__)


class NewsSource:
    def __init__(self, name: str, url: str, type: str = "rss"):
        self.name = name
        self.url = url
        self.type = type


class WebSearchService:
    def __init__(self):
        # Use HTTPS + stable, high-signal feeds
        self.news_sources = [
            NewsSource("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
            NewsSource("Reuters", "https://feeds.reuters.com/reuters/topNews"),
            NewsSource(
                "AP News (Top)", "https://rsshub.app/ap/topics/apf-topnews"
            ),  # may be flaky; keep as optional
            NewsSource(
                "CNN", "http://rss.cnn.com/rss/edition.rss"
            ),  # CNN still serves HTTP RSS reliably
            NewsSource("NPR", "https://feeds.npr.org/1001/rss.xml"),
        ]
        self.max_articles = 5
        self.search_timeout = 15
        self._headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NewsFetcher/1.0; +https://example.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self._stopwords = set(
            """
            a an and are as at be but by for from has have if in into is it of on or that the to was were will with
        """.split()
        )

    async def search_recent_news(
        self, topic: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for recent news articles related to the topic."""
        rss_articles = await self._search_rss_feeds(topic, max_results)
        articles = list(rss_articles)

        if len(articles) < max_results:
            web_articles = await self._search_web(topic, max_results - len(articles))
            articles.extend(web_articles)

        # Deduplicate by URL/title and sort by date desc
        seen = set()
        deduped = []
        for a in articles:
            key = a.get("url") or a.get("title")
            if key and key not in seen:
                seen.add(key)
                deduped.append(a)

        deduped.sort(
            key=lambda x: x.get("published")
            or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return deduped[:max_results]

    async def _search_rss_feeds(
        self, topic: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Search RSS feeds for topic-related articles (concurrently)."""
        async with httpx.AsyncClient(
            timeout=self.search_timeout, headers=self._headers, follow_redirects=True
        ) as client:
            tasks = [
                self._fetch_rss_articles(client, source, topic)
                for source in self.news_sources
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        articles: List[Dict[str, Any]] = []
        for source, result in zip(self.news_sources, results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to fetch from {source.name}: {result}")
                continue
            articles.extend(result)

        # Keep only recent and sort
        articles = self._filter_recent_articles(articles)
        return articles[:max_results]

    async def _fetch_rss_articles(
        self, client: httpx.AsyncClient, source: "NewsSource", topic: str
    ) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed."""
        try:
            resp = await client.get(source.url)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            logger.error(f"Error fetching RSS from {source.name}: {e}")
            return []

        results: List[Dict[str, Any]] = []
        for entry in feed.entries[:20]:  # check a few more; we’ll filter later
            if not self._is_topic_relevant(entry, topic):
                continue

            title = entry.get("title", "") or ""
            summary = entry.get("summary", "") or ""
            url = entry.get("link", "") or ""

            dt = self._parse_entry_datetime(entry)

            results.append(
                {
                    "title": title,
                    "summary": self._clean_text(summary),
                    "url": url,
                    "published": dt,
                    "source": source.name,
                }
            )

        return results

    async def _search_web(self, topic: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Best-effort fallback using DuckDuckGo Instant Answer.
        Note: This is NOT a proper news API and may return sparse results.
        """
        if max_results <= 0:
            return []

        articles: List[Dict[str, Any]] = []
        search_query = f"{topic} news"
        url = f"https://api.duckduckgo.com/?q={quote(search_query)}&format=json&no_html=1&skip_disambig=1"

        try:
            async with httpx.AsyncClient(
                timeout=self.search_timeout, headers=self._headers
            ) as client:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()

            # Try multiple buckets DDG returns
            candidates: Iterable[Dict[str, Any]] = []

            if isinstance(data.get("RelatedTopics"), list):
                candidates = candidates + [
                    it for it in data["RelatedTopics"] if isinstance(it, dict)
                ]
            if isinstance(data.get("Results"), list):
                candidates = list(candidates) + [
                    it for it in data["Results"] if isinstance(it, dict)
                ]
            # Sometimes there's a main Abstract + AbstractURL
            if data.get("Abstract") and data.get("AbstractURL"):
                candidates = list(candidates) + [
                    {"Text": data["Abstract"], "FirstURL": data["AbstractURL"]}
                ]

            for item in candidates:
                text = (item.get("Text") or "").strip()
                link = (item.get("FirstURL") or "").strip()
                if not text or not link:
                    continue
                if not self._is_text_relevant(text, topic):
                    continue

                articles.append(
                    {
                        "title": (text[:100] + "...") if len(text) > 100 else text,
                        "summary": text,
                        "url": link,
                        "published": datetime.now(timezone.utc),
                        "source": "DuckDuckGo",
                    }
                )
                if len(articles) >= max_results:
                    break

        except Exception as e:
            logger.error(f"Web search failed: {e}")

        return articles

    # ---------- helpers ----------

    def _tokenize(self, s: str) -> List[str]:
        return [
            t
            for t in re.findall(r"[A-Za-z0-9]+", s.lower())
            if len(t) > 2 and t not in self._stopwords
        ]

    def _is_text_relevant(self, text: str, topic: str) -> bool:
        t_tokens = set(self._tokenize(text))
        q_tokens = set(self._tokenize(topic))
        if not q_tokens:
            return True
        # require at least one overlapping token (tweakable)
        return len(t_tokens & q_tokens) > 0

    def _is_topic_relevant(self, entry: Dict[str, Any], topic: str) -> bool:
        title = entry.get("title", "") or ""
        summary = entry.get("summary", "") or entry.get("description", "") or ""
        return self._is_text_relevant(f"{title} {summary}", topic)

    def _parse_entry_datetime(self, entry: Dict[str, Any]) -> Optional[datetime]:
        """
        Prefer feedparser's normalized *_parsed fields, then ISO/HTTP dates via email.utils.
        Always return timezone-aware UTC when possible.
        """
        tm = entry.get("published_parsed") or entry.get("updated_parsed")
        if tm:
            try:
                return datetime(*tm[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        for key in ("published", "updated", "dc:date", "date"):
            val = entry.get(key)
            if not val:
                continue
            try:
                dt = parsedate_to_datetime(val)
                # Ensure tz-aware
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                continue

        return None  # no date → let recent filter drop it

    def _filter_recent_articles(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent = [
            a for a in articles if a.get("published") and a["published"] >= cutoff
        ]
        recent.sort(
            key=lambda x: x.get("published")
            or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return recent

    async def get_article_content(self, url: str) -> Optional[str]:
        """Extract full article content from URL (best-effort)."""
        try:
            async with httpx.AsyncClient(
                timeout=self.search_timeout,
                headers=self._headers,
                follow_redirects=True,
            ) as client:
                r = await client.get(url)
                r.raise_for_status()
                soup = BeautifulSoup(r.content, "html.parser")

            # Remove script/style/noscript
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            # Prefer main/article tags if present
            main = soup.find("article") or soup.find("main") or soup.body
            text = (
                main.get_text(separator=" ", strip=True)
                if main
                else soup.get_text(separator=" ", strip=True)
            )

            # Collapse whitespace and limit
            text = re.sub(r"\s+", " ", text).strip()
            return text[:2000] if text else None

        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return None

    def _clean_text(self, s: str) -> str:
        return re.sub(r"\s+", " ", (s or "")).strip()

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
