from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, name: str, model: str, temperature: float = 0.7):
        self.name = name
        self.model = model
        self.temperature = temperature

    @abstractmethod
    async def generate_hot_take(self, topic: str, style: str = "controversial") -> str:
        pass

    @abstractmethod
    def get_system_prompt(self, style: str) -> str:
        pass