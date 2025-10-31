from typing import List
from app.agents.openai_agent import OpenAIAgent
from app.agents.anthropic_agent import AnthropicAgent
from app.models.schemas import HotTakeResponse
from app.services.web_search_service import WebSearchService
from app.core.prompts import PromptManager
import random


class HotTakeService:
    def __init__(self):
        self.agents = {"openai": OpenAIAgent(), "anthropic": AnthropicAgent()}
        self.web_search_service = WebSearchService()

    async def generate_hot_take(
        self,
        topic: str,
        style: str = "controversial",
        agent_type: str = None,
        use_web_search: bool = False,
        max_articles: int = 3,
    ) -> HotTakeResponse:
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            agent = random.choice(list(self.agents.values()))

        news_context = None
        if use_web_search:
            try:
                news_context = await self.web_search_service.search_and_format(
                    topic, max_articles
                )
            except Exception as e:
                # If web search fails, continue without it
                print(f"Web search failed: {e}")
                news_context = None

        hot_take = await agent.generate_hot_take(topic, style, news_context)

        return HotTakeResponse(
            hot_take=hot_take,
            topic=topic,
            style=style,
            agent_used=agent.name,
            web_search_used=use_web_search and news_context is not None,
            news_context=news_context if use_web_search else None,
        )

    def get_available_agents(self) -> List[str]:
        return list(self.agents.keys())

    def get_available_styles(self) -> List[str]:
        return PromptManager.get_all_available_styles()
