from anthropic import AsyncAnthropic
from app.agents.base import BaseAgent
from app.core.config import settings

class AnthropicAgent(BaseAgent):
    def __init__(self, name: str = "Claude Agent", model: str = "claude-3-haiku-20240307", temperature: float = 0.8):
        super().__init__(name, model, temperature)
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_hot_take(self, topic: str, style: str = "controversial") -> str:
        system_prompt = self.get_system_prompt(style)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Generate a hot take about: {topic}"}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Error generating hot take: {str(e)}"

    def get_system_prompt(self, style: str) -> str:
        prompts = {
            "controversial": "You are a provocative opinion generator. Create bold, controversial takes that challenge conventional wisdom. Be edgy but thoughtful.",
            "analytical": "You are a deep analytical thinker. Generate hot takes that break down complex topics with nuanced analysis.",
            "philosophical": "You are a modern philosopher. Generate hot takes that question fundamental assumptions about life and society.",
            "witty": "You are a clever wordsmith. Generate hot takes that are clever, punchy, and memorable.",
            "contrarian": "You are a professional contrarian. Always take the opposite stance from popular opinion, but back it up with reasoning."
        }
        return prompts.get(style, prompts["controversial"])