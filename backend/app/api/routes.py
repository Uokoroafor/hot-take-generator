import logging
from fastapi import APIRouter, HTTPException, Response
from app.models.schemas import HotTakeRequest, HotTakeResponse
from app.observability.langfuse import get_current_trace_id, start_request_span
from app.services.hot_take_service import HotTakeService

router = APIRouter()
hot_take_service = HotTakeService()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=HotTakeResponse)
async def generate_hot_take(request: HotTakeRequest, response: Response):
    payload = request.model_dump(exclude_none=True)
    with start_request_span(
        name="api.generate_hot_take",
        input_data=payload,
        metadata={
            "feature": "hot_take_generator",
            "route": "/api/generate",
        },
    ) as span:
        try:
            result = await hot_take_service.generate_hot_take(
                topic=request.topic,
                style=request.style,
                agent_type=request.agent_type,
                use_web_search=request.use_web_search,
                use_news_search=request.use_news_search,
                max_articles=request.max_articles,
                web_search_provider=request.web_search_provider,
                news_days=request.news_days,
                strict_quality_mode=request.strict_quality_mode,
            )
            if span and hasattr(span, "update"):
                span.update(
                    output={
                        "agent_used": result.agent_used,
                        "web_search_used": result.web_search_used,
                        "sources_count": len(result.sources or []),
                    }
                )

            trace_id = get_current_trace_id()
            if trace_id:
                response.headers["X-Trace-Id"] = trace_id

            return result
        except Exception as e:
            logger.exception("Failed to generate hot take")
            raise HTTPException(
                status_code=500, detail="Failed to generate hot take. Please try again."
            ) from e


@router.get("/agents")
async def get_agents():
    return {"agents": hot_take_service.get_available_agents_metadata()}


@router.get("/styles")
async def get_styles():
    return {"styles": hot_take_service.get_available_styles()}
