"""Tests for the SSE streaming endpoint and service."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status

from app.models.schemas import (
    DoneEvent,
    ErrorEvent,
    SourceRecord,
    SourcesEvent,
    StatusEvent,
    TokenEvent,
)
from app.services.hot_take_service import HotTakeService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_sse_lines(raw: bytes) -> list[dict]:
    """Parse raw SSE bytes into a list of parsed JSON event dicts."""
    events = []
    for line in raw.decode().splitlines():
        line = line.strip()
        if line.startswith("data: "):
            payload = line[len("data: ") :]
            if payload:
                events.append(json.loads(payload))
    return events


async def async_token_generator(*tokens: str):
    """Async generator that yields the provided tokens."""
    for token in tokens:
        yield token


# ---------------------------------------------------------------------------
# Schema model tests
# ---------------------------------------------------------------------------


class TestStreamEventSchemas:
    def test_status_event_serialisation(self):
        event = StatusEvent(message="Searching the web...")
        data = json.loads(event.model_dump_json())
        assert data["type"] == "status"
        assert data["message"] == "Searching the web..."

    def test_token_event_serialisation(self):
        event = TokenEvent(text="hot ")
        data = json.loads(event.model_dump_json())
        assert data["type"] == "token"
        assert data["text"] == "hot "

    def test_sources_event_serialisation(self):
        src = SourceRecord(type="web", title="Test", url="https://example.com")
        event = SourcesEvent(sources=[src])
        data = json.loads(event.model_dump_json())
        assert data["type"] == "sources"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["url"] == "https://example.com"

    def test_done_event_serialisation(self):
        event = DoneEvent(
            hot_take="Hot take text",
            topic="test",
            style="controversial",
            agent_used="Claude Agent",
        )
        data = json.loads(event.model_dump_json())
        assert data["type"] == "done"
        assert data["hot_take"] == "Hot take text"
        assert data["web_search_used"] is False

    def test_error_event_serialisation(self):
        event = ErrorEvent(detail="Something went wrong")
        data = json.loads(event.model_dump_json())
        assert data["type"] == "error"
        assert data["detail"] == "Something went wrong"


# ---------------------------------------------------------------------------
# Service streaming tests
# ---------------------------------------------------------------------------


class TestStreamHotTakeService:
    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_stream_emits_status_then_tokens_then_done(
        self, mock_anthropic_cls, mock_openai_cls
    ):
        mock_agent = MagicMock()
        mock_agent.name = "OpenAI Agent"
        mock_agent.model = "gpt-4.1-mini"
        mock_agent.temperature = 0.8
        mock_agent.generate_hot_take_stream = MagicMock(
            return_value=async_token_generator("Hot ", "take!")
        )
        mock_openai_cls.return_value = mock_agent
        mock_anthropic_cls.return_value = MagicMock()

        service = HotTakeService()
        # Disable cache for this test
        service.cache.get_random_variant = AsyncMock(return_value=(None, 0))
        service.cache.add_variant = AsyncMock(return_value=1)

        events = []
        async for chunk in service.stream_hot_take(
            topic="test topic", style="controversial", agent_type="openai"
        ):
            if chunk.startswith("data: "):
                events.append(json.loads(chunk[len("data: ") :]))

        types = [e["type"] for e in events]
        assert "status" in types
        assert "token" in types
        assert "done" in types
        assert types[-1] == "done"

        token_texts = [e["text"] for e in events if e["type"] == "token"]
        assert "".join(token_texts) == "Hot take!"

        done_event = next(e for e in events if e["type"] == "done")
        assert done_event["hot_take"] == "Hot take!"
        assert done_event["topic"] == "test topic"
        assert done_event["agent_used"] == "OpenAI Agent"

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_stream_emits_sources_before_tokens(
        self, mock_anthropic_cls, mock_openai_cls
    ):
        mock_agent = MagicMock()
        mock_agent.name = "OpenAI Agent"
        mock_agent.model = "gpt-4.1-mini"
        mock_agent.temperature = 0.8
        mock_agent.generate_hot_take_stream = MagicMock(
            return_value=async_token_generator("take")
        )
        mock_openai_cls.return_value = mock_agent
        mock_anthropic_cls.return_value = MagicMock()

        service = HotTakeService()
        service.web_search_service.search = AsyncMock(
            return_value=[
                {
                    "title": "Article",
                    "url": "https://example.com",
                    "snippet": "snippet",
                    "source": "example.com",
                }
            ]
        )
        service.web_search_service.format_search_context = MagicMock(
            return_value="web context"
        )

        events = []
        async for chunk in service.stream_hot_take(
            topic="test topic",
            style="controversial",
            agent_type="openai",
            use_web_search=True,
        ):
            if chunk.startswith("data: "):
                events.append(json.loads(chunk[len("data: ") :]))

        types = [e["type"] for e in events]
        assert "sources" in types
        # sources must come before any token
        sources_idx = next(i for i, e in enumerate(events) if e["type"] == "sources")
        first_token_idx = next(
            (i for i, e in enumerate(events) if e["type"] == "token"), len(events)
        )
        assert sources_idx < first_token_idx

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_stream_cache_hit_replays_as_tokens(
        self, mock_anthropic_cls, mock_openai_cls
    ):
        mock_agent = MagicMock()
        mock_agent.name = "OpenAI Agent"
        mock_openai_cls.return_value = mock_agent
        mock_anthropic_cls.return_value = MagicMock()

        service = HotTakeService()
        service.cache.max_variants = 5
        service.cache.get_random_variant = AsyncMock(
            return_value=(
                {
                    "hot_take": "Cached hot take",
                    "topic": "test",
                    "style": "controversial",
                    "agent_used": "OpenAI Agent",
                    "web_search_used": False,
                    "news_context": None,
                    "sources": None,
                },
                5,
            )
        )

        events = []
        async for chunk in service.stream_hot_take(
            topic="test", style="controversial", agent_type="openai"
        ):
            if chunk.startswith("data: "):
                events.append(json.loads(chunk[len("data: ") :]))

        types = [e["type"] for e in events]
        assert "token" in types
        assert "done" in types
        # Should not have called the real agent
        mock_agent.generate_hot_take_stream.assert_not_called()

        token_texts = [e["text"] for e in events if e["type"] == "token"]
        assert "".join(token_texts).strip() == "Cached hot take"

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_stream_emits_error_event_on_agent_failure(
        self, mock_anthropic_cls, mock_openai_cls
    ):
        async def failing_generator(*args, **kwargs):
            raise RuntimeError("Agent exploded")
            yield  # pragma: no cover

        mock_agent = MagicMock()
        mock_agent.name = "OpenAI Agent"
        mock_agent.model = "gpt-4.1-mini"
        mock_agent.temperature = 0.8
        mock_agent.generate_hot_take_stream = MagicMock(
            return_value=failing_generator()
        )
        mock_openai_cls.return_value = mock_agent
        mock_anthropic_cls.return_value = MagicMock()

        service = HotTakeService()
        service.cache.get_random_variant = AsyncMock(return_value=(None, 0))

        events = []
        async for chunk in service.stream_hot_take(
            topic="test", style="controversial", agent_type="openai"
        ):
            if chunk.startswith("data: "):
                events.append(json.loads(chunk[len("data: ") :]))

        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) == 1
        assert "Generation failed" in error_events[0]["detail"]

    @pytest.mark.asyncio
    @patch("app.services.hot_take_service.start_generation_observation")
    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    async def test_stream_updates_generation_observation_on_success(
        self,
        mock_anthropic_cls,
        mock_openai_cls,
        mock_start_generation_observation,
    ):
        mock_agent = MagicMock()
        mock_agent.name = "OpenAI Agent"
        mock_agent.model = "gpt-4.1-mini"
        mock_agent.temperature = 0.8
        mock_agent.generate_hot_take_stream = MagicMock(
            return_value=async_token_generator("Hot ", "take!")
        )
        mock_openai_cls.return_value = mock_agent
        mock_anthropic_cls.return_value = MagicMock()

        generation_obj = MagicMock()
        generation_cm = MagicMock()
        generation_cm.__enter__.return_value = generation_obj
        generation_cm.__exit__.return_value = False
        mock_start_generation_observation.return_value = generation_cm

        service = HotTakeService()
        service.cache.get_random_variant = AsyncMock(return_value=(None, 0))
        service.cache.add_variant = AsyncMock(return_value=1)

        async for _chunk in service.stream_hot_take(
            topic="test topic", style="controversial", agent_type="openai"
        ):
            pass

        mock_start_generation_observation.assert_called_once()
        generation_obj.update.assert_called_once()
        update_kwargs = generation_obj.update.call_args.kwargs
        assert update_kwargs["output"] == "Hot take!"
        assert update_kwargs["metadata"]["stream_completed"] is True


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


class TestStreamingEndpoint:
    @patch("app.services.hot_take_service.HotTakeService.stream_hot_take")
    def test_stream_endpoint_returns_event_stream(self, mock_stream, client):
        async def fake_stream(**kwargs):
            yield f"data: {StatusEvent(message='Generating...').model_dump_json()}\n\n"
            yield f"data: {TokenEvent(text='Hot take!').model_dump_json()}\n\n"
            yield (
                f"data: {DoneEvent(hot_take='Hot take!', topic='test', style='controversial', agent_used='Test Agent').model_dump_json()}\n\n"
            )

        mock_stream.return_value = fake_stream()

        response = client.post(
            "/api/generate/stream",
            json={"topic": "test topic", "style": "controversial"},
            headers={"Accept": "text/event-stream"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in response.headers["content-type"]

        events = parse_sse_lines(response.content)
        assert any(e["type"] == "status" for e in events)
        assert any(e["type"] == "token" for e in events)
        assert any(e["type"] == "done" for e in events)

    def test_stream_endpoint_rejects_missing_topic(self, client):
        response = client.post(
            "/api/generate/stream",
            json={"style": "controversial"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_stream_endpoint_rejects_empty_topic(self, client):
        response = client.post(
            "/api/generate/stream",
            json={"topic": ""},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_stream_endpoint_payload_too_large(self, client):
        response = client.post(
            "/api/generate/stream",
            json={"topic": "x" * 20000},
        )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "too large" in response.json()["detail"]

    def test_stream_endpoint_rate_limit(self, client):
        """The streaming endpoint shares the same rate limiter as /api/generate."""
        with patch(
            "app.services.hot_take_service.HotTakeService.stream_hot_take"
        ) as mock_stream:

            async def fake_stream(**kwargs):
                yield f"data: {DoneEvent(hot_take='t', topic='t', style='controversial', agent_used='A').model_dump_json()}\n\n"

            # Exhaust the rate limit
            from app.core.config import settings

            limit = settings.generate_rate_limit_per_minute
            for _ in range(limit):
                mock_stream.return_value = fake_stream()
                client.post("/api/generate/stream", json={"topic": "test"})

            # Next request should be rate-limited
            mock_stream.return_value = fake_stream()
            response = client.post("/api/generate/stream", json={"topic": "test"})
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @patch("app.services.hot_take_service.HotTakeService.stream_hot_take")
    def test_stream_endpoint_handles_service_error(self, mock_stream, client):
        # Reset in-memory rate limit state so this test isn't affected by the
        # rate-limit test that runs before it.
        import app.main as main_module

        main_module.request_timestamps_by_ip.clear()

        async def error_stream(**kwargs):
            yield f"data: {ErrorEvent(detail='Generation failed. Please try again.').model_dump_json()}\n\n"

        mock_stream.return_value = error_stream()

        response = client.post(
            "/api/generate/stream",
            json={"topic": "test topic"},
        )

        assert response.status_code == status.HTTP_200_OK
        events = parse_sse_lines(response.content)
        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) == 1

    @patch("app.api.routes.get_current_trace_id")
    @patch("app.services.hot_take_service.HotTakeService.stream_hot_take")
    def test_stream_endpoint_sets_trace_header(
        self, mock_stream, mock_get_current_trace_id, client
    ):
        async def fake_stream(**kwargs):
            yield f"data: {DoneEvent(hot_take='t', topic='x', style='controversial', agent_used='A').model_dump_json()}\n\n"

        mock_stream.return_value = fake_stream()
        mock_get_current_trace_id.return_value = "trace-stream-123"

        response = client.post("/api/generate/stream", json={"topic": "test topic"})
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("x-trace-id") == "trace-stream-123"
