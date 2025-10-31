from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


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
    def get_system_prompt(self, style: str, with_news: bool = False) -> str:
        pass

    def format_prompt_with_news(self, topic: str, news_context: Optional[str]) -> str:
        """Format the user prompt to include news context if available"""
        if news_context:
            return f"""Topic: {topic}

Recent news context:
{news_context}

Based on the above recent news and current context, generate a hot take about: {topic}"""
        else:
            return f"Generate a hot take about: {topic}"
