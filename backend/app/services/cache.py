import json
import logging
import random
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self._client = None
        self.max_variants = max(1, settings.cache_variant_pool_size)
        if settings.redis_url:
            try:
                import redis.asyncio as aioredis

                self._client = aioredis.from_url(
                    settings.redis_url, decode_responses=True
                )
                logger.info("Redis cache enabled")
            except Exception as e:
                logger.warning("Redis connection failed, caching disabled: %s", e)
        else:
            logger.info("No REDIS_URL configured, caching disabled")

    def _make_key(self, topic: str, style: str, agent_type: Optional[str]) -> str:
        topic_norm = topic.lower().strip()
        if agent_type:
            return f"hot_take:{topic_norm}:{style}:{agent_type}"
        return f"hot_take:{topic_norm}:{style}"

    def _normalize_pool(self, raw_data: str) -> list[dict]:
        parsed = json.loads(raw_data)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            return [parsed]
        return []

    def _dedupe_and_trim(self, variants: list[dict]) -> list[dict]:
        deduped: list[dict] = []
        seen = set()
        for item in variants:
            try:
                fingerprint = json.dumps(item, sort_keys=True)
            except TypeError:
                continue
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            deduped.append(item)
        return deduped[-self.max_variants :]

    async def get_random_variant(
        self, topic: str, style: str, agent_type: Optional[str]
    ) -> tuple[Optional[dict], int]:
        if not self._client:
            return None, 0
        try:
            key = self._make_key(topic, style, agent_type)
            data = await self._client.get(key)
            if data:
                variants = self._normalize_pool(data)
                if not variants:
                    return None, 0
                logger.debug("Cache hit: %s (variants=%d)", key, len(variants))
                return random.choice(variants), len(variants)
        except Exception as e:
            logger.warning("Cache get failed: %s", e)
        return None, 0

    async def add_variant(
        self, topic: str, style: str, agent_type: Optional[str], value: dict
    ) -> int:
        if not self._client:
            return 0
        try:
            key = self._make_key(topic, style, agent_type)
            existing_raw = await self._client.get(key)
            variants = []
            if existing_raw:
                variants = self._normalize_pool(existing_raw)
            variants.append(value)
            variants = self._dedupe_and_trim(variants)
            await self._client.setex(
                key, settings.cache_ttl_seconds, json.dumps(variants)
            )
            logger.debug(
                "Cache set: %s (variants=%d ttl=%ds)",
                key,
                len(variants),
                settings.cache_ttl_seconds,
            )
            return len(variants)
        except Exception as e:
            logger.warning("Cache set failed: %s", e)
            return 0
