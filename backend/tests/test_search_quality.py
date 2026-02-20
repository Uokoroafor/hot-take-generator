from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.search_quality import (
    SearchQualityConfig,
    apply_recency_window,
    coerce_float,
    dedupe_records,
    domain_allowed,
    extract_domain,
    normalize_url,
    parse_date_string,
    parse_domain_list,
    score_record,
    tokenize,
)


class TestParseDomainList:
    def test_csv_input(self):
        result = parse_domain_list("reuters.com,bbc.com,nytimes.com")
        assert result == {"reuters.com", "bbc.com", "nytimes.com"}

    def test_strips_whitespace(self):
        result = parse_domain_list(" reuters.com , bbc.com ")
        assert result == {"reuters.com", "bbc.com"}

    def test_strips_www_prefix(self):
        result = parse_domain_list("www.reuters.com,www.bbc.com")
        assert result == {"reuters.com", "bbc.com"}

    def test_lowercases(self):
        result = parse_domain_list("Reuters.COM,BBC.com")
        assert result == {"reuters.com", "bbc.com"}

    def test_empty_string(self):
        assert parse_domain_list("") == set()

    def test_none_input(self):
        assert parse_domain_list(None) == set()

    def test_blank_entries_ignored(self):
        result = parse_domain_list("reuters.com,,  ,bbc.com")
        assert result == {"reuters.com", "bbc.com"}


class TestCoerceFloat:
    def test_valid_float(self):
        assert coerce_float(0.5, 1.0) == 0.5

    def test_valid_int(self):
        assert coerce_float(3, 1.0) == 3.0

    def test_valid_string(self):
        assert coerce_float("0.75", 1.0) == 0.75

    def test_invalid_string(self):
        assert coerce_float("not_a_number", 0.5) == 0.5

    def test_none_returns_default(self):
        assert coerce_float(None, 0.6) == 0.6


class TestExtractDomain:
    def test_full_url(self):
        assert extract_domain("https://www.reuters.com/article/123") == "reuters.com"

    def test_bare_domain(self):
        assert extract_domain("reuters.com") == "reuters.com"

    def test_www_prefix_stripped(self):
        assert extract_domain("www.bbc.com") == "bbc.com"

    def test_empty_string(self):
        assert extract_domain("") == ""

    def test_http_url(self):
        assert extract_domain("http://example.com/path") == "example.com"

    def test_uppercase_normalized(self):
        assert extract_domain("HTTPS://WWW.BBC.COM/news") == "bbc.com"


class TestNormalizeUrl:
    def test_strips_trailing_slash(self):
        result = normalize_url("https://example.com/path/")
        assert result == "example.com/path"

    def test_strips_www(self):
        result = normalize_url("https://www.example.com/page")
        assert result == "example.com/page"

    def test_empty_string(self):
        assert normalize_url("") == ""

    def test_lowercases_domain(self):
        result = normalize_url("https://EXAMPLE.COM/Page")
        assert "example.com" in result


class TestParseDateString:
    def test_iso_format(self):
        result = parse_date_string("2024-11-01T10:00:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 11
        assert result.day == 1

    def test_iso_with_offset(self):
        result = parse_date_string("2024-11-01T10:00:00+00:00")
        assert result is not None
        assert result.tzinfo is not None

    def test_relative_days_ago(self):
        now = datetime(2024, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("3 days ago", now=now)
        assert result is not None
        assert result == now - timedelta(days=3)

    def test_relative_hours_ago(self):
        now = datetime(2024, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("5 hours ago", now=now)
        assert result == now - timedelta(hours=5)

    def test_relative_weeks_ago(self):
        now = datetime(2024, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("2 weeks ago", now=now)
        assert result == now - timedelta(weeks=2)

    def test_relative_minutes_ago(self):
        now = datetime(2024, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("30 minutes ago", now=now)
        assert result == now - timedelta(minutes=30)

    def test_relative_month_ago(self):
        now = datetime(2024, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("1 month ago", now=now)
        assert result == now - timedelta(days=30)

    def test_relative_year_ago(self):
        now = datetime(2024, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("1 year ago", now=now)
        assert result == now - timedelta(days=365)

    def test_common_date_format_short_month(self):
        result = parse_date_string("Nov 01, 2024")
        assert result is not None
        assert result.year == 2024
        assert result.month == 11

    def test_common_date_format_full_month(self):
        result = parse_date_string("November 01, 2024")
        assert result is not None
        assert result.month == 11

    def test_yyyy_mm_dd_format(self):
        result = parse_date_string("2024-11-01")
        assert result is not None
        assert result.year == 2024

    def test_none_input(self):
        assert parse_date_string(None) is None

    def test_empty_string(self):
        assert parse_date_string("") is None

    def test_unparseable_string(self):
        assert parse_date_string("not a date at all") is None


class TestTokenize:
    def test_basic_tokenization(self):
        tokens = tokenize("Hello World 2024")
        assert "hello" in tokens
        assert "world" in tokens
        assert "2024" in tokens

    def test_short_tokens_excluded(self):
        tokens = tokenize("I am a developer")
        assert "am" in tokens
        assert "developer" in tokens
        # Single char "I" and "a" should be excluded (< 2 chars)
        assert "i" not in tokens
        assert "a" not in tokens

    def test_empty_string(self):
        assert tokenize("") == set()

    def test_none_input(self):
        assert tokenize(None) == set()

    def test_lowercases(self):
        tokens = tokenize("AI Technology")
        assert "ai" in tokens
        assert "technology" in tokens


class TestDomainAllowed:
    def test_allowed_no_lists(self):
        assert domain_allowed("reuters.com", set(), set()) is True

    def test_blocked_by_blocklist(self):
        assert domain_allowed("spam.com", set(), {"spam.com"}) is False

    def test_allowed_by_allowlist(self):
        assert domain_allowed("reuters.com", {"reuters.com"}, set()) is True

    def test_rejected_by_allowlist(self):
        assert domain_allowed("other.com", {"reuters.com"}, set()) is False

    def test_empty_domain(self):
        assert domain_allowed("", set(), set()) is False

    def test_full_url_domain(self):
        assert domain_allowed("https://www.reuters.com/article", set(), set()) is True

    def test_blocklist_takes_precedence(self):
        assert domain_allowed("spam.com", {"spam.com"}, {"spam.com"}) is False


class TestDedupeRecords:
    def test_dedupes_by_url(self):
        records = [
            {"title": "Article 1", "url": "https://example.com/a"},
            {"title": "Article 2", "url": "https://example.com/a"},
        ]
        result = dedupe_records(records)
        assert len(result) == 1
        assert result[0]["title"] == "Article 1"

    def test_dedupes_by_title_when_no_url(self):
        records = [
            {"title": "Same Title", "url": ""},
            {"title": "Same Title", "url": ""},
        ]
        result = dedupe_records(records)
        assert len(result) == 1

    def test_preserves_unique(self):
        records = [
            {"title": "Article 1", "url": "https://example.com/a"},
            {"title": "Article 2", "url": "https://example.com/b"},
        ]
        result = dedupe_records(records)
        assert len(result) == 2

    def test_empty_list(self):
        assert dedupe_records([]) == []

    def test_www_normalization(self):
        records = [
            {"title": "Article 1", "url": "https://www.example.com/a"},
            {"title": "Article 2", "url": "https://example.com/a"},
        ]
        result = dedupe_records(records)
        assert len(result) == 1


class TestApplyRecencyWindow:
    def test_filters_old_articles(self):
        now = datetime.now(timezone.utc)
        records = [
            {"title": "Recent", "published": now - timedelta(days=2)},
            {"title": "Old", "published": now - timedelta(days=30)},
        ]
        result = apply_recency_window(records, days_back=7)
        assert len(result) == 1
        assert result[0]["title"] == "Recent"

    def test_keeps_articles_without_dates(self):
        now = datetime.now(timezone.utc)
        records = [
            {"title": "No date", "published": None},
            {"title": "Recent", "published": now - timedelta(days=1)},
        ]
        result = apply_recency_window(records, days_back=7)
        assert len(result) == 2

    def test_zero_days_returns_all(self):
        now = datetime.now(timezone.utc)
        records = [
            {"title": "Old", "published": now - timedelta(days=365)},
        ]
        result = apply_recency_window(records, days_back=0)
        assert len(result) == 1

    def test_naive_datetime_treated_as_utc(self):
        naive_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=2)
        records = [
            {"title": "Naive", "published": naive_date},
        ]
        result = apply_recency_window(records, days_back=7)
        assert len(result) == 1


class TestScoreRecord:
    def _default_kwargs(self):
        return {
            "topic_tokens": tokenize("artificial intelligence"),
            "topic_text": "artificial intelligence",
            "trusted_domains": {"reuters.com", "bbc.com"},
            "recency_days": 14,
            "strict_quality_mode": False,
        }

    def test_relevant_record_scores_higher(self):
        relevant = {
            "title": "Artificial Intelligence breakthrough",
            "snippet": "New AI intelligence model released today",
            "source": "reuters.com",
            "published": datetime.now(timezone.utc) - timedelta(days=1),
        }
        irrelevant = {
            "title": "Cooking recipes for dinner",
            "snippet": "Best pasta recipes for family meals",
            "source": "recipes.com",
            "published": datetime.now(timezone.utc) - timedelta(days=1),
        }
        score_relevant = score_record(relevant, **self._default_kwargs())
        score_irrelevant = score_record(irrelevant, **self._default_kwargs())
        assert score_relevant > score_irrelevant

    def test_trusted_domain_scores_higher(self):
        trusted = {
            "title": "AI news update",
            "snippet": "Artificial intelligence developments",
            "source": "reuters.com",
            "published": datetime.now(timezone.utc),
        }
        untrusted = {
            "title": "AI news update",
            "snippet": "Artificial intelligence developments",
            "source": "randomblog.com",
            "published": datetime.now(timezone.utc),
        }
        kwargs = self._default_kwargs()
        assert score_record(trusted, **kwargs) > score_record(untrusted, **kwargs)

    def test_recent_scores_higher_than_old(self):
        recent = {
            "title": "AI artificial intelligence news",
            "snippet": "Latest developments",
            "source": "example.com",
            "published": datetime.now(timezone.utc) - timedelta(hours=6),
        }
        old = {
            "title": "AI artificial intelligence news",
            "snippet": "Latest developments",
            "source": "example.com",
            "published": datetime.now(timezone.utc) - timedelta(days=13),
        }
        kwargs = self._default_kwargs()
        assert score_record(recent, **kwargs) > score_record(old, **kwargs)

    def test_strict_mode_penalizes_no_overlap(self):
        record = {
            "title": "Cooking recipes",
            "snippet": "Best pasta recipes",
            "source": "food.com",
            "published": datetime.now(timezone.utc),
        }
        kwargs = self._default_kwargs()
        normal_score = score_record(record, **{**kwargs, "strict_quality_mode": False})
        strict_score = score_record(record, **{**kwargs, "strict_quality_mode": True})
        assert strict_score < normal_score

    def test_longer_snippet_scores_higher(self):
        short = {
            "title": "AI artificial intelligence",
            "snippet": "Short",
            "source": "example.com",
            "published": None,
        }
        long = {
            "title": "AI artificial intelligence",
            "snippet": "A " * 60 + "artificial intelligence developments and news",
            "source": "example.com",
            "published": None,
        }
        kwargs = self._default_kwargs()
        assert score_record(long, **kwargs) > score_record(short, **kwargs)

    def test_no_published_date_gets_low_recency(self):
        record = {
            "title": "AI artificial intelligence",
            "snippet": "News about AI developments",
            "source": "example.com",
            "published": None,
        }
        score = score_record(record, **self._default_kwargs())
        assert score > 0  # Should still have a positive score


class TestSearchQualityConfig:
    def test_loads_defaults_from_settings(self):
        settings = SimpleNamespace(
            search_domain_allowlist="",
            search_domain_blocklist="",
            search_trusted_domains="reuters.com,bbc.com",
            search_score_weight_relevance=0.60,
            search_score_weight_recency=0.20,
            search_score_weight_snippet=0.10,
            search_score_weight_domain=0.10,
            search_score_strict_no_overlap_penalty=0.35,
        )
        config = SearchQualityConfig(settings)
        assert config.allowlist == set()
        assert config.blocklist == set()
        assert config.trusted_domains == {"reuters.com", "bbc.com"}
        assert config.score_weights["relevance_weight"] == 0.60
        assert config.score_weights["recency_weight"] == 0.20

    def test_handles_missing_attributes(self):
        settings = SimpleNamespace()
        config = SearchQualityConfig(settings)
        assert config.allowlist == set()
        assert config.blocklist == set()
        assert config.trusted_domains == set()
        assert config.score_weights["relevance_weight"] == 0.60

    def test_parses_allowlist_and_blocklist(self):
        settings = SimpleNamespace(
            search_domain_allowlist="reuters.com,bbc.com",
            search_domain_blocklist="spam.com",
            search_trusted_domains="",
            search_score_weight_relevance=0.60,
            search_score_weight_recency=0.20,
            search_score_weight_snippet=0.10,
            search_score_weight_domain=0.10,
            search_score_strict_no_overlap_penalty=0.35,
        )
        config = SearchQualityConfig(settings)
        assert config.allowlist == {"reuters.com", "bbc.com"}
        assert config.blocklist == {"spam.com"}
