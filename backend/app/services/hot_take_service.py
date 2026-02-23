import logging
import random
from typing import Any, AsyncIterator, Dict, List, Optional

from app.agents.anthropic_agent import AnthropicAgent
from app.agents.openai_agent import OpenAIAgent
from app.core.prompts import PromptManager
from app.models.schemas import (
    AgentConfig,
    DoneEvent,
    ErrorEvent,
    HotTakeResponse,
    SourceRecord,
    SourcesEvent,
    StatusEvent,
    TokenEvent,
)
from app.observability.langfuse import start_generation_observation
from app.services.cache import CacheService
from app.services.news_search_service import NewsSearchService
from app.services.web_search_service import WebSearchService

logger = logging.getLogger(__name__)


class HotTakeService:
    def __init__(self):
        self.agents = {"openai": OpenAIAgent(), "anthropic": AnthropicAgent()}
        self.web_search_service = WebSearchService()
        self.news_search_service = NewsSearchService()
        self.cache = CacheService()

    async def generate_hot_take(
        self,
        topic: str,
        style: str = "controversial",
        agent_type: str = None,
        use_web_search: bool = False,
        use_news_search: bool = False,
        max_articles: int = 3,
        web_search_provider: Optional[str] = None,
        news_days: Optional[int] = None,
        strict_quality_mode: bool = False,
    ) -> HotTakeResponse:
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            agent = random.choice(list(self.agents.values()))

        # Check cache for no-search requests only.
        # Strategy: keep generating fresh takes until variant pool is full,
        # then serve a random cached variant.
        use_search = use_web_search or use_news_search
        cache_pool_size = 0
        if not use_search:
            cached, cache_pool_size = await self.cache.get_random_variant(
                topic, style, agent_type
            )
            if cached and cache_pool_size >= self.cache.max_variants:
                cached_response = HotTakeResponse.model_validate(cached)
                with start_generation_observation(
                    name="llm.generate_hot_take",
                    input_data={
                        "topic": topic,
                        "style": style,
                        "has_context": False,
                    },
                    metadata={
                        "agent_type": agent_type or "random",
                        "agent_name": cached_response.agent_used,
                        "use_web_search": use_web_search,
                        "use_news_search": use_news_search,
                        "news_days": news_days,
                        "strict_quality_mode": strict_quality_mode,
                        "cache_hit": True,
                        "cache_pool_size": cache_pool_size,
                    },
                    model="cache",
                    model_parameters={},
                ) as generation:
                    if generation and hasattr(generation, "update"):
                        generation.update(
                            output=cached_response.hot_take,
                            metadata={
                                "cache_hit": True,
                                "sources_count": len(cached_response.sources or []),
                            },
                        )
                return cached_response

        # Gather context from various sources
        context_parts = []
        source_records: List[SourceRecord] = []

        # Web search context (general web results)
        if use_web_search:
            try:
                # Create service with specific provider if requested
                if web_search_provider:
                    web_service = WebSearchService(provider_name=web_search_provider)
                else:
                    web_service = self.web_search_service

                web_results = await web_service.search(
                    topic,
                    max_articles,
                    strict_quality_mode=strict_quality_mode,
                )
                web_context = web_service.format_search_context(web_results)
                if web_context and "No web search results" not in web_context:
                    context_parts.append(web_context)
                source_records.extend(self._build_web_source_records(web_results))
            except Exception as e:
                logger.warning("Web search failed: %s", e)

        # News search context (news articles)
        news_context = None
        if use_news_search:
            try:
                news_articles = await self.news_search_service.search_recent_news(
                    topic,
                    max_articles,
                    days_back=news_days,
                    strict_quality_mode=strict_quality_mode,
                )
                news_context = self.news_search_service.format_news_context(
                    news_articles
                )
                if news_context and "No recent news found" not in news_context:
                    context_parts.append(news_context)
                source_records.extend(self._build_news_source_records(news_articles))
            except Exception as e:
                logger.warning("News search failed: %s", e)

        # Combine all context
        combined_context = "\n\n".join(context_parts) if context_parts else None

        with start_generation_observation(
            name="llm.generate_hot_take",
            input_data={
                "topic": topic,
                "style": style,
                "has_context": bool(combined_context),
            },
            metadata={
                "agent_type": agent_type or "random",
                "agent_name": agent.name,
                "use_web_search": use_web_search,
                "use_news_search": use_news_search,
                "news_days": news_days,
                "strict_quality_mode": strict_quality_mode,
                "cache_hit": False,
                "cache_pool_size": cache_pool_size,
            },
            model=agent.model,
            model_parameters={
                "temperature": agent.temperature,
                "max_tokens": 250 if combined_context else 200,
            },
        ) as generation:
            hot_take = await agent.generate_hot_take(topic, style, combined_context)
            if generation and hasattr(generation, "update"):
                generation.update(
                    output=hot_take,
                    metadata={"sources_count": len(source_records)},
                )

        result = HotTakeResponse(
            hot_take=hot_take,
            topic=topic,
            style=style,
            agent_used=agent.name,
            web_search_used=use_search and combined_context is not None,
            news_context=combined_context if use_search else None,
            sources=source_records if source_records else None,
        )

        if not use_search:
            cache_pool_size = await self.cache.add_variant(
                topic, style, agent_type, result.model_dump(mode="json")
            )
            logger.debug(
                "Cached non-search take for topic='%s' style='%s' (pool_size=%d)",
                topic,
                style,
                cache_pool_size,
            )

        return result

    async def stream_hot_take(
        self,
        topic: str,
        style: str = "controversial",
        agent_type: str = None,
        use_web_search: bool = False,
        use_news_search: bool = False,
        max_articles: int = 3,
        web_search_provider: Optional[str] = None,
        news_days: Optional[int] = None,
        strict_quality_mode: bool = False,
    ) -> AsyncIterator[str]:
        """Async generator yielding SSE-formatted event strings."""

        def sse(event) -> str:
            return f"data: {event.model_dump_json()}\n\n"

        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            agent = random.choice(list(self.agents.values()))

        use_search = use_web_search or use_news_search

        # Cache check (non-search requests only)
        if not use_search:
            cached, cache_pool_size = await self.cache.get_random_variant(
                topic, style, agent_type
            )
            if cached and cache_pool_size >= self.cache.max_variants:
                cached_response = HotTakeResponse.model_validate(cached)
                yield sse(StatusEvent(message="Serving cached take..."))
                # Replay cached text as fake token chunks for consistent UX
                words = cached_response.hot_take.split()
                for i, word in enumerate(words):
                    suffix = " " if i < len(words) - 1 else ""
                    yield sse(TokenEvent(text=word + suffix))
                yield sse(
                    DoneEvent(
                        hot_take=cached_response.hot_take,
                        topic=cached_response.topic,
                        style=cached_response.style,
                        agent_used=cached_response.agent_used,
                        web_search_used=cached_response.web_search_used,
                        news_context=cached_response.news_context,
                        sources=cached_response.sources,
                    )
                )
                return

        # Search phase
        context_parts: List[str] = []
        source_records: List[SourceRecord] = []

        if use_web_search:
            yield sse(StatusEvent(message="Searching the web..."))
            try:
                web_service = (
                    WebSearchService(provider_name=web_search_provider)
                    if web_search_provider
                    else self.web_search_service
                )
                web_results = await web_service.search(
                    topic, max_articles, strict_quality_mode=strict_quality_mode
                )
                web_context = web_service.format_search_context(web_results)
                if web_context and "No web search results" not in web_context:
                    context_parts.append(web_context)
                source_records.extend(self._build_web_source_records(web_results))
            except Exception as e:
                logger.warning("Web search failed: %s", e)

        if use_news_search:
            yield sse(StatusEvent(message="Searching recent news..."))
            try:
                news_articles = await self.news_search_service.search_recent_news(
                    topic,
                    max_articles,
                    days_back=news_days,
                    strict_quality_mode=strict_quality_mode,
                )
                news_context = self.news_search_service.format_news_context(
                    news_articles
                )
                if news_context and "No recent news found" not in news_context:
                    context_parts.append(news_context)
                source_records.extend(self._build_news_source_records(news_articles))
            except Exception as e:
                logger.warning("News search failed: %s", e)

        # Emit sources before generation starts so the UI can show them
        if source_records:
            yield sse(SourcesEvent(sources=source_records))

        combined_context = "\n\n".join(context_parts) if context_parts else None

        yield sse(StatusEvent(message=f"Generating with {agent.name}..."))

        # Stream LLM tokens
        tokens: List[str] = []
        hot_take = ""
        with start_generation_observation(
            name="llm.generate_hot_take_stream",
            input_data={
                "topic": topic,
                "style": style,
                "has_context": bool(combined_context),
            },
            metadata={
                "agent_type": agent_type or "random",
                "agent_name": agent.name,
                "use_web_search": use_web_search,
                "use_news_search": use_news_search,
                "news_days": news_days,
                "strict_quality_mode": strict_quality_mode,
                "cache_hit": False,
                "streaming": True,
            },
            model=agent.model,
            model_parameters={
                "temperature": agent.temperature,
                "max_tokens": 250 if combined_context else 200,
            },
        ) as generation:
            try:
                async for token in agent.generate_hot_take_stream(
                    topic, style, combined_context
                ):
                    tokens.append(token)
                    yield sse(TokenEvent(text=token))
            except Exception:
                logger.exception("Streaming generation failed")
                if generation and hasattr(generation, "update"):
                    generation.update(
                        output="",
                        metadata={
                            "stream_completed": False,
                            "sources_count": len(source_records),
                        },
                    )
                yield sse(ErrorEvent(detail="Generation failed. Please try again."))
                return

            hot_take = "".join(tokens).strip()
            if generation and hasattr(generation, "update"):
                generation.update(
                    output=hot_take,
                    metadata={
                        "stream_completed": True,
                        "sources_count": len(source_records),
                    },
                )

        result = HotTakeResponse(
            hot_take=hot_take,
            topic=topic,
            style=style,
            agent_used=agent.name,
            web_search_used=use_search and combined_context is not None,
            news_context=combined_context if use_search else None,
            sources=source_records if source_records else None,
        )

        # Cache non-search results
        if not use_search:
            cache_pool_size = await self.cache.add_variant(
                topic, style, agent_type, result.model_dump(mode="json")
            )
            logger.debug(
                "Cached streaming take for topic='%s' style='%s' (pool_size=%d)",
                topic,
                style,
                cache_pool_size,
            )

        yield sse(
            DoneEvent(
                hot_take=hot_take,
                topic=topic,
                style=style,
                agent_used=agent.name,
                web_search_used=result.web_search_used,
                news_context=result.news_context,
                sources=result.sources,
            )
        )

    def get_available_agents(self) -> List[str]:
        return list(self.agents.keys())

    def get_available_agents_metadata(self) -> List[AgentConfig]:
        descriptions = {
            "openai": "Generates hot takes with OpenAI models.",
            "anthropic": "Generates hot takes with Anthropic Claude models.",
        }
        return [
            AgentConfig(
                id=agent_id,
                name=agent.name,
                description=descriptions.get(agent_id, "AI agent"),
                model=agent.model,
                temperature=agent.temperature,
                system_prompt=agent.get_system_prompt("controversial"),
            )
            for agent_id, agent in self.agents.items()
        ]

    def get_available_styles(self) -> List[str]:
        return PromptManager.get_all_available_styles()

    def _build_web_source_records(
        self, results: List[Dict[str, Any]]
    ) -> List[SourceRecord]:
        records: List[SourceRecord] = []
        for result in results:
            title = result.get("title", "").strip()
            url = result.get("url", "").strip()
            if not title or not url:
                continue
            records.append(
                SourceRecord(
                    type="web",
                    title=title,
                    url=url,
                    snippet=result.get("snippet", "") or None,
                    source=result.get("source", "") or None,
                    published=result.get("published"),
                )
            )
        return records

    def _build_news_source_records(
        self, articles: List[Dict[str, Any]]
    ) -> List[SourceRecord]:
        records: List[SourceRecord] = []
        for article in articles:
            title = article.get("title", "").strip()
            url = article.get("url", "").strip()
            if not title or not url:
                continue
            records.append(
                SourceRecord(
                    type="news",
                    title=title,
                    url=url,
                    snippet=article.get("summary", "") or None,
                    source=article.get("source", "") or None,
                    published=article.get("published"),
                )
            )
        return records
