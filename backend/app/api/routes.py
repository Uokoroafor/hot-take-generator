from fastapi import APIRouter, HTTPException
from app.models.schemas import HotTakeRequest, HotTakeResponse
from app.services.hot_take_service import HotTakeService

router = APIRouter()
hot_take_service = HotTakeService()


@router.post("/generate", response_model=HotTakeResponse)
async def generate_hot_take(request: HotTakeRequest):
    try:
        result = await hot_take_service.generate_hot_take(
            topic=request.topic,
            style=request.style,
            agent_type=request.agent_type,
            use_web_search=request.use_web_search,
            use_news_search=request.use_news_search,
            max_articles=request.max_articles,
            web_search_provider=request.web_search_provider,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agents():
    return {"agents": hot_take_service.get_available_agents_metadata()}


@router.get("/styles")
async def get_styles():
    return {"styles": hot_take_service.get_available_styles()}
