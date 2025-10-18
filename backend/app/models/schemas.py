from pydantic import BaseModel
from typing import Optional, List

class HotTakeRequest(BaseModel):
    topic: str
    style: Optional[str] = "controversial"
    length: Optional[str] = "medium"

class HotTakeResponse(BaseModel):
    hot_take: str
    topic: str
    style: str
    agent_used: str

class AgentConfig(BaseModel):
    name: str
    description: str
    model: str
    temperature: float
    system_prompt: str