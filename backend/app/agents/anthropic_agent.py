from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.agents.base import BaseAgent
from app.core.config import settings
from app.core.prompts import PromptManager, AgentType


class AnthropicAgent(BaseAgent):
    def __init__(
        self,
        name: str = "Claude Agent",
        model: str = "claude-haiku-4-5-20251001",
        temperature: float = 0.8,
    ):
        super().__init__(name, model, temperature)
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_hot_take(
        self, topic: str, style: str = "controversial", news_context: str = None
    ) -> str:
        system_prompt = self.get_system_prompt(style, with_news=bool(news_context))
        user_prompt = self.format_prompt_with_news(topic, news_context)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=250 if news_context else 200,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError("Anthropic generation failed") from e

    async def generate_hot_take_stream(
        self, topic: str, style: str = "controversial", news_context: str = None
    ) -> AsyncIterator[str]:
        system_prompt = self.get_system_prompt(style, with_news=bool(news_context))
        user_prompt = self.format_prompt_with_news(topic, news_context)

        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=250 if news_context else 200,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise RuntimeError("Anthropic streaming generation failed") from e

    def get_system_prompt(self, style: str, with_news: bool = False) -> str:
        return PromptManager.get_full_prompt(AgentType.ANTHROPIC, style, with_news)
