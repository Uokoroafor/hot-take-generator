import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.cache import CacheService


@pytest.mark.asyncio
async def test_cache_returns_none_when_client_missing():
    service = CacheService()
    service._client = None

    value, pool_size = await service.get_random_variant("ai", "witty", "openai")

    assert value is None
    assert pool_size == 0


@pytest.mark.asyncio
async def test_cache_get_random_variant_from_legacy_single_value():
    service = CacheService()
    service._client = AsyncMock()
    service._client.get.return_value = json.dumps(
        {
            "hot_take": "Legacy entry",
            "topic": "ai",
            "style": "witty",
            "agent_used": "OpenAI Agent",
        }
    )

    with patch(
        "app.services.cache.random.choice",
        side_effect=lambda values: values[0],
    ):
        value, pool_size = await service.get_random_variant("ai", "witty", "openai")

    assert value is not None
    assert value["hot_take"] == "Legacy entry"
    assert pool_size == 1


@pytest.mark.asyncio
async def test_cache_add_variant_dedupes_and_trims_pool():
    service = CacheService()
    service._client = AsyncMock()
    service.max_variants = 2

    existing = [
        {
            "hot_take": "Take one",
            "topic": "ai",
            "style": "witty",
            "agent_used": "OpenAI Agent",
        },
        {
            "hot_take": "Take two",
            "topic": "ai",
            "style": "witty",
            "agent_used": "OpenAI Agent",
        },
    ]
    service._client.get.return_value = json.dumps(existing)

    pool_size = await service.add_variant(
        "ai",
        "witty",
        "openai",
        {
            "hot_take": "Take two",
            "topic": "ai",
            "style": "witty",
            "agent_used": "OpenAI Agent",
        },
    )

    assert pool_size == 2
    service._client.setex.assert_called_once()
    saved_payload = service._client.setex.call_args.args[2]
    saved_variants = json.loads(saved_payload)
    assert len(saved_variants) == 2
    assert [item["hot_take"] for item in saved_variants] == ["Take one", "Take two"]
