from anthropic import AsyncAnthropic
from app.agents.base import BaseAgent
from app.core.config import settings

class AnthropicAgent(BaseAgent):
    def __init__(self, name: str = "Claude Agent", model: str = "claude-3-haiku-20240307", temperature: float = 0.8):
        super().__init__(name, model, temperature)
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_hot_take(self, topic: str, style: str = "controversial", news_context: str = None) -> str:
        system_prompt = self.get_system_prompt(style, with_news=bool(news_context))
        user_prompt = self.format_prompt_with_news(topic, news_context)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=250 if news_context else 200,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Error generating hot take: {str(e)}"

    def get_system_prompt(self, style: str, with_news: bool = False) -> str:
        base_prompts = {
            "controversial": "You are a provocative opinion generator. Create bold, controversial takes that challenge conventional wisdom. Be edgy but thoughtful.",
            "analytical": "You are a deep analytical thinker. Generate hot takes that break down complex topics with nuanced analysis.",
            "philosophical": "You are a modern philosopher. Generate hot takes that question fundamental assumptions about life and society.",
            "witty": "You are a clever wordsmith. Generate hot takes that are clever, punchy, and memorable.",
            "contrarian": "You are a professional contrarian. Always take the opposite stance from popular opinion, but back it up with reasoning."
        }

        base_prompt = base_prompts.get(style, base_prompts["controversial"])

        if with_news:
            base_prompt += " When provided with recent news context, weave those current events into your analysis to create a hot take that's both timely and insightful. Use the news as evidence or counterpoints to support your perspective."

        return base_prompt