from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional


class BaseAgent(ABC):
    def __init__(self, name: str, model: str, temperature: float = 0.7):
        self.name = name
        self.model = model
        self.temperature = temperature

    @abstractmethod
    async def generate_hot_take(
        self,
        topic: str,
        style: str = "controversial",
        news_context: Optional[str] = None,
    ) -> str:
        pass

    @abstractmethod
    async def generate_hot_take_stream(
        self,
        topic: str,
        style: str = "controversial",
        news_context: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Stream hot take tokens. Subclasses implement as async generators."""
        raise NotImplementedError  # pragma: no cover
        yield  # pragma: no cover  # marks this as an async generator in the type system

    @abstractmethod
    def get_system_prompt(self, style: str, with_news: bool = False) -> str:
        pass

    def format_prompt_with_news(self, topic: str, news_context: Optional[str]) -> str:
        """Format the user prompt to include news context if available"""
        if news_context:
            return f"""Topic: {topic}

Recent news context:
{news_context}

Instructions:
- Base your take on the strongest evidence in the context.
- Ignore low-signal details and unsupported claims.
- If sources disagree, briefly note the tension.
- Keep it punchy, but fact-grounded.

Generate a hot take about: {topic}"""
        else:
            return f"Generate a hot take about: {topic}"
