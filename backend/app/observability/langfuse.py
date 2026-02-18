import logging
from contextlib import nullcontext
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from langfuse import Langfuse
except ImportError:  # pragma: no cover
    Langfuse = None  # type: ignore[assignment]

_langfuse_client: Any | None = None
_langfuse_initialized = False


def get_langfuse_client() -> Any | None:
    global _langfuse_client, _langfuse_initialized

    if _langfuse_initialized:
        return _langfuse_client

    _langfuse_initialized = True

    if not settings.langfuse_tracing_enabled:
        return None

    if Langfuse is None:
        logger.info("Langfuse SDK not installed. Tracing is disabled.")
        return None

    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        logger.info("Langfuse keys not configured. Tracing is disabled.")
        return None

    try:
        _langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    except Exception:
        logger.exception("Failed to initialize Langfuse client.")
        _langfuse_client = None

    return _langfuse_client


def start_request_span(
    *, name: str, input_data: dict[str, Any], metadata: dict[str, Any]
) -> Any:
    client = get_langfuse_client()
    if not client:
        return nullcontext(None)
    return client.start_as_current_span(name=name, input=input_data, metadata=metadata)


def start_generation_observation(
    *,
    name: str,
    input_data: dict[str, Any],
    metadata: dict[str, Any],
    model: str,
    model_parameters: dict[str, Any],
) -> Any:
    client = get_langfuse_client()
    if not client:
        return nullcontext(None)
    return client.start_as_current_observation(
        name=name,
        as_type="generation",
        input=input_data,
        metadata=metadata,
        model=model,
        model_parameters=model_parameters,
    )


def get_current_trace_id() -> str | None:
    client = get_langfuse_client()
    if not client:
        return None
    try:
        return client.get_current_trace_id()
    except Exception:
        logger.exception("Failed to read current Langfuse trace id.")
        return None


def flush_langfuse() -> None:
    client = get_langfuse_client()
    if not client:
        return
    try:
        client.flush()
    except Exception:
        logger.exception("Failed to flush Langfuse client.")
