from typing import Dict, List
from app.agents.openai_agent import OpenAIAgent
from app.agents.anthropic_agent import AnthropicAgent
from app.models.schemas import HotTakeResponse
import random

class HotTakeService:
    def __init__(self):
        self.agents = {
            "openai": OpenAIAgent(),
            "anthropic": AnthropicAgent()
        }

    async def generate_hot_take(self, topic: str, style: str = "controversial", agent_type: str = None) -> HotTakeResponse:
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            agent = random.choice(list(self.agents.values()))

        hot_take = await agent.generate_hot_take(topic, style)

        return HotTakeResponse(
            hot_take=hot_take,
            topic=topic,
            style=style,
            agent_used=agent.name
        )

    def get_available_agents(self) -> List[str]:
        return list(self.agents.keys())

    def get_available_styles(self) -> List[str]:
        return ["controversial", "sarcastic", "optimistic", "pessimistic", "absurd", "analytical", "philosophical", "witty", "contrarian"]