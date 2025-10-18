from openai import AsyncOpenAI
from app.agents.base import BaseAgent
from app.core.config import settings

class OpenAIAgent(BaseAgent):
    def __init__(self, name: str = "OpenAI Agent", model: str = "gpt-3.5-turbo", temperature: float = 0.8):
        super().__init__(name, model, temperature)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_hot_take(self, topic: str, style: str = "controversial") -> str:
        system_prompt = self.get_system_prompt(style)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a hot take about: {topic}"}
                ],
                temperature=self.temperature,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating hot take: {str(e)}"

    def get_system_prompt(self, style: str) -> str:
        prompts = {
            "controversial": "You are a provocative opinion generator. Create bold, controversial takes that challenge conventional wisdom. Be edgy but not offensive.",
            "sarcastic": "You are a sarcastic commentator. Generate witty, sarcastic hot takes with a sharp sense of humor.",
            "optimistic": "You are an optimistic contrarian. Generate positive, uplifting hot takes that find the good in everything.",
            "pessimistic": "You are a cynical realist. Generate pessimistic hot takes that highlight the worst-case scenarios.",
            "absurd": "You are an absurdist philosopher. Generate completely ridiculous and absurd hot takes that make people laugh."
        }
        return prompts.get(style, prompts["controversial"])