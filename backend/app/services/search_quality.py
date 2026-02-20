from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set
from urllib.parse import urlparse


_TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
_RELATIVE_TIME_RE = re.compile(
    r"(?P<count>\d+)\s+(?P<unit>minute|hour|day|week|month|year)s?\s+ago",
    re.IGNORECASE,
)


def parse_domain_list(raw: str) -> Set[str]:
    if not raw or not isinstance(raw, str):
        return set()
    return {
        entry.strip().lower().removeprefix("www.")
        for entry in raw.split(",")
        if entry.strip()
    }


def coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def extract_domain(value: str) -> str:
    if not value:
        return ""
    domain = value.strip().lower()
    if "://" in domain:
        parsed = urlparse(domain)
        domain = parsed.netloc.lower()
    return domain.removeprefix("www.")


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    normalized_netloc = parsed.netloc.lower().removeprefix("www.")
    normalized_path = parsed.path.rstrip("/")
    return f"{normalized_netloc}{normalized_path}"


def parse_date_string(
    value: Optional[str], now: Optional[datetime] = None
) -> Optional[datetime]:
    if not value:
        return None

    now = now or datetime.now(timezone.utc)
    raw = value.strip()

    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        pass

    relative_match = _RELATIVE_TIME_RE.search(raw)
    if relative_match:
        count = int(relative_match.group("count"))
        unit = relative_match.group("unit").lower()
        if unit == "minute":
            return now - timedelta(minutes=count)
        if unit == "hour":
            return now - timedelta(hours=count)
        if unit == "day":
            return now - timedelta(days=count)
        if unit == "week":
            return now - timedelta(weeks=count)
        if unit == "month":
            return now - timedelta(days=count * 30)
        if unit == "year":
            return now - timedelta(days=count * 365)

    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def tokenize(text: str) -> Set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


class SearchQualityConfig:
    """Shared search quality settings loaded from app config."""

    def __init__(self, app_settings: Any) -> None:
        self.allowlist = parse_domain_list(
            getattr(app_settings, "search_domain_allowlist", "")
        )
        self.blocklist = parse_domain_list(
            getattr(app_settings, "search_domain_blocklist", "")
        )
        self.trusted_domains = parse_domain_list(
            getattr(app_settings, "search_trusted_domains", "")
        )
        self.score_weights = {
            "relevance_weight": coerce_float(
                getattr(app_settings, "search_score_weight_relevance", 0.60), 0.60
            ),
            "recency_weight": coerce_float(
                getattr(app_settings, "search_score_weight_recency", 0.20), 0.20
            ),
            "snippet_weight": coerce_float(
                getattr(app_settings, "search_score_weight_snippet", 0.10), 0.10
            ),
            "domain_weight": coerce_float(
                getattr(app_settings, "search_score_weight_domain", 0.10), 0.10
            ),
            "strict_no_overlap_penalty": coerce_float(
                getattr(app_settings, "search_score_strict_no_overlap_penalty", 0.35),
                0.35,
            ),
        }


def domain_allowed(domain: str, allowlist: Set[str], blocklist: Set[str]) -> bool:
    normalized = extract_domain(domain)
    if not normalized:
        return False
    if normalized in blocklist:
        return False
    if allowlist and normalized not in allowlist:
        return False
    return True


def dedupe_records(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for record in records:
        key = normalize_url(record.get("url", "")) or record.get("title", "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def apply_recency_window(
    records: Iterable[Dict[str, Any]], days_back: int, date_key: str = "published"
) -> List[Dict[str, Any]]:
    if days_back <= 0:
        return list(records)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    filtered: List[Dict[str, Any]] = []
    for record in records:
        published = record.get(date_key)
        if not published:
            filtered.append(record)
            continue
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        if published >= cutoff:
            filtered.append(record)
    return filtered


def _recency_score(published: Optional[datetime], max_days: int) -> float:
    if not published:
        return 0.12
    published_utc = (
        published.replace(tzinfo=timezone.utc)
        if published.tzinfo is None
        else published.astimezone(timezone.utc)
    )
    age_days = max(
        0.0, (datetime.now(timezone.utc) - published_utc).total_seconds() / 86400.0
    )
    if age_days >= max_days:
        return 0.0
    return max(0.0, 1.0 - (age_days / max_days))


def score_record(
    record: Dict[str, Any],
    *,
    topic_tokens: Set[str],
    topic_text: str,
    trusted_domains: Set[str],
    recency_days: int,
    strict_quality_mode: bool,
    relevance_weight: float = 0.60,
    recency_weight: float = 0.20,
    snippet_weight: float = 0.10,
    domain_weight: float = 0.10,
    strict_no_overlap_penalty: float = 0.35,
) -> float:
    title = record.get("title", "")
    snippet = record.get("snippet", "") or record.get("summary", "")
    domain = extract_domain(record.get("source") or record.get("url", ""))
    published = record.get("published")

    text_tokens = tokenize(f"{title} {snippet}")
    overlap = len(topic_tokens & text_tokens)
    relevance_score = min(1.0, overlap / max(1, min(len(topic_tokens), 6)))
    title_l = title.lower()
    topic_l = (topic_text or "").strip().lower()
    exact_phrase_boost = 0.08 if topic_l and topic_l in title_l else 0.0

    snippet_len = len(snippet.strip())
    snippet_quality = 0.0
    if snippet_len >= 50:
        snippet_quality = 0.5
    if snippet_len >= 100:
        snippet_quality = 1.0

    domain_quality = 0.35 if domain in trusted_domains else 0.15
    recency_score = _recency_score(published, max(7, recency_days))

    total = (
        (relevance_score * relevance_weight)
        + (recency_score * recency_weight)
        + (snippet_quality * snippet_weight)
        + (domain_quality * domain_weight)
        + exact_phrase_boost
    )

    if strict_quality_mode and overlap == 0:
        total -= strict_no_overlap_penalty
    return total
