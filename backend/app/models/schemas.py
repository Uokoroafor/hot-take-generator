from pydantic import BaseModel, field_validator
from typing import Optional, List, Literal, Union
from datetime import datetime


class HotTakeRequest(BaseModel):
    topic: str
    style: Optional[str] = "controversial"
    length: Optional[str] = "medium"
    agent_type: Optional[str] = None  # 'openai', 'anthropic', or None for random
    use_web_search: Optional[bool] = False
    use_news_search: Optional[bool] = False
    max_articles: Optional[int] = 3
    web_search_provider: Optional[str] = None  # 'brave', 'serper', or None for auto
    news_days: Optional[int] = 14
    strict_quality_mode: Optional[bool] = False

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()

    @field_validator("web_search_provider")
    @classmethod
    def validate_provider(cls, v):
        if v and v not in ["brave", "serper"]:
            raise ValueError("web_search_provider must be 'brave', 'serper', or None")
        return v

    @field_validator("agent_type")
    @classmethod
    def validate_agent_type(cls, v):
        if v and v not in ["openai", "anthropic"]:
            raise ValueError("agent_type must be 'openai', 'anthropic', or None")
        return v

    @field_validator("news_days")
    @classmethod
    def validate_news_days(cls, v):
        if v is None:
            return v
        if v < 1 or v > 90:
            raise ValueError("news_days must be between 1 and 90")
        return v


class SourceRecord(BaseModel):
    type: Literal["web", "news"]
    title: str
    url: str
    snippet: Optional[str] = None
    source: Optional[str] = None
    published: Optional[datetime] = None


class HotTakeResponse(BaseModel):
    hot_take: str
    topic: str
    style: str
    agent_used: str
    web_search_used: Optional[bool] = False
    news_context: Optional[str] = None
    sources: Optional[List[SourceRecord]] = None

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
    id: str
    name: str
    description: str
    model: str
    temperature: float
    system_prompt: str


# --- SSE streaming event types ---


class StatusEvent(BaseModel):
    type: Literal["status"] = "status"
    message: str


class SourcesEvent(BaseModel):
    type: Literal["sources"] = "sources"
    sources: List[SourceRecord]


class TokenEvent(BaseModel):
    type: Literal["token"] = "token"
    text: str


class DoneEvent(BaseModel):
    type: Literal["done"] = "done"
    hot_take: str
    topic: str
    style: str
    agent_used: str
    web_search_used: Optional[bool] = False
    news_context: Optional[str] = None
    sources: Optional[List[SourceRecord]] = None


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    detail: str


StreamEvent = Union[StatusEvent, SourcesEvent, TokenEvent, DoneEvent, ErrorEvent]
