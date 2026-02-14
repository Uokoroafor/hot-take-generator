from typing import List, Optional
from app.agents.openai_agent import OpenAIAgent
from app.agents.anthropic_agent import AnthropicAgent
from app.models.schemas import HotTakeResponse, AgentConfig
from app.services.web_search_service import WebSearchService
from app.services.news_search_service import NewsSearchService
from app.core.prompts import PromptManager
import random


class HotTakeService:
    def __init__(self):
        self.agents = {"openai": OpenAIAgent(), "anthropic": AnthropicAgent()}
        self.web_search_service = WebSearchService()
        self.news_search_service = NewsSearchService()

    async def generate_hot_take(
        self,
        topic: str,
        style: str = "controversial",
        agent_type: str = None,
        use_web_search: bool = False,
        use_news_search: bool = False,
        max_articles: int = 3,
        web_search_provider: Optional[str] = None,
    ) -> HotTakeResponse:
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            agent = random.choice(list(self.agents.values()))

        # Gather context from various sources
        context_parts = []

        # Web search context (general web results)
        if use_web_search:
            try:
                # Create service with specific provider if requested
                if web_search_provider:
                    web_service = WebSearchService(provider_name=web_search_provider)
                else:
                    web_service = self.web_search_service

                web_context = await web_service.search_and_format(topic, max_articles)
                if web_context and "No web search results" not in web_context:
                    context_parts.append(web_context)
            except Exception as e:
                print(f"Web search failed: {e}")

        # News search context (news articles)
        news_context = None
        if use_news_search:
            try:
                news_context = await self.news_search_service.search_and_format(
                    topic, max_articles
                )
                if news_context and "No recent news found" not in news_context:
                    context_parts.append(news_context)
            except Exception as e:
                print(f"News search failed: {e}")

        # Combine all context
        combined_context = "\n\n".join(context_parts) if context_parts else None

        hot_take = await agent.generate_hot_take(topic, style, combined_context)

        return HotTakeResponse(
            hot_take=hot_take,
            topic=topic,
            style=style,
            agent_used=agent.name,
            web_search_used=(use_web_search or use_news_search)
            and combined_context is not None,
            news_context=combined_context
            if (use_web_search or use_news_search)
            else None,
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
