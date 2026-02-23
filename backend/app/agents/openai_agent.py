from typing import AsyncIterator

from openai import AsyncOpenAI

from app.agents.base import BaseAgent
from app.core.config import settings
from app.core.prompts import PromptManager, AgentType


class OpenAIAgent(BaseAgent):
    def __init__(
        self,
        name: str = "OpenAI Agent",
        model: str = "gpt-4.1-mini",
        temperature: float = 0.8,
    ):
        super().__init__(name, model, temperature)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_hot_take(
        self, topic: str, style: str = "controversial", news_context: str = None
    ) -> str:
        system_prompt = self.get_system_prompt(style, with_news=bool(news_context))
        user_prompt = self.format_prompt_with_news(topic, news_context)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=250 if news_context else 200,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError("OpenAI generation failed") from e

    async def generate_hot_take_stream(
        self, topic: str, style: str = "controversial", news_context: str = None
    ) -> AsyncIterator[str]:
        system_prompt = self.get_system_prompt(style, with_news=bool(news_context))
        user_prompt = self.format_prompt_with_news(topic, news_context)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=250 if news_context else 200,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            raise RuntimeError("OpenAI streaming generation failed") from e

    def get_system_prompt(self, style: str, with_news: bool = False) -> str:
        return PromptManager.get_full_prompt(AgentType.OPENAI, style, with_news)
