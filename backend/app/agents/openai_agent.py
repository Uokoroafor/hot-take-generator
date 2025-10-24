from openai import AsyncOpenAI
from app.agents.base import BaseAgent
from app.core.config import settings

class OpenAIAgent(BaseAgent):
    def __init__(self, name: str = "OpenAI Agent", model: str = "gpt-3.5-turbo", temperature: float = 0.8):
        super().__init__(name, model, temperature)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_hot_take(self, topic: str, style: str = "controversial", news_context: str = None) -> str:
        system_prompt = self.get_system_prompt(style, with_news=bool(news_context))
        user_prompt = self.format_prompt_with_news(topic, news_context)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=250 if news_context else 200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating hot take: {str(e)}"

    def get_system_prompt(self, style: str, with_news: bool = False) -> str:
        base_prompts = {
            "controversial": "You are a provocative opinion generator. Create bold, controversial takes that challenge conventional wisdom. Be edgy but not offensive.",
            "sarcastic": "You are a sarcastic commentator. Generate witty, sarcastic hot takes with a sharp sense of humor.",
            "optimistic": "You are an optimistic contrarian. Generate positive, uplifting hot takes that find the good in everything.",
            "pessimistic": "You are a cynical realist. Generate pessimistic hot takes that highlight the worst-case scenarios.",
            "absurd": "You are an absurdist philosopher. Generate completely ridiculous and absurd hot takes that make people laugh."
        }

        base_prompt = base_prompts.get(style, base_prompts["controversial"])

        if with_news:
            base_prompt += " When provided with recent news context, incorporate those current events and developments into your hot take to make it timely and relevant. Reference specific news items when they support your argument."

        return base_prompt