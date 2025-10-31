from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class HotTakeRequest(BaseModel):
    topic: str
    style: Optional[str] = "controversial"
    length: Optional[str] = "medium"
    use_web_search: Optional[bool] = False
    max_articles: Optional[int] = 3

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()


class HotTakeResponse(BaseModel):
    hot_take: str
    topic: str
    style: str
    agent_used: str
    web_search_used: Optional[bool] = False
    news_context: Optional[str] = None

    @field_validator("hot_take", "topic", "style", "agent_used")
    def not_empty_or_whitespace(cls, v: str, field):
        if not v or not v.strip():
            raise ValueError(f"{str(field)} cannot be empty or whitespace")
        return v.strip()


class NewsArticle(BaseModel):
    title: str
    summary: Optional[str] = None
    url: str
    published: Optional[datetime] = None
    source: str


class WebSearchResult(BaseModel):
    articles: List[NewsArticle]
    search_query: str
    total_found: int


class AgentConfig(BaseModel):
    name: str
    description: str
    model: str
    temperature: float
    system_prompt: str
