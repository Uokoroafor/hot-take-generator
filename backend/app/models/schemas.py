from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class HotTakeRequest(BaseModel):
    topic: str
    style: Optional[str] = "controversial"
    length: Optional[str] = "medium"
    use_web_search: Optional[bool] = False
    max_articles: Optional[int] = 3

class HotTakeResponse(BaseModel):
    hot_take: str
    topic: str
    style: str
    agent_used: str
    web_search_used: Optional[bool] = False
    news_context: Optional[str] = None

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