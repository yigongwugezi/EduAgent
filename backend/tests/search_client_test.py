import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.search_client import (
    MockSearchClient,
    SearchError,
    SearchResponse,
    SearchResultItem,
    search_cache,
    get_search_client,
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


# ── MockSearchClient ───────────────────────────────────────────────────────


def test_mock_search_returns_results() -> None:
    client = MockSearchClient()
    response = client.search("Python neural networks")
    assert_true(len(response.results) > 0, "mock search should return results")
    assert_equal(response.source, "mock", "source should be mock")
    assert_true(
        "Mock Result" in response.results[0].title,
        "title should contain mock prefix",
    )


def test_mock_search_respects_max_results() -> None:
    client = MockSearchClient()
    response = client.search("test", max_results=2)
    assert_true(len(response.results) <= 2, "max_results should be respected")


def test_mock_search_available() -> None:
    client = MockSearchClient()
    assert_true(client.is_available(), "mock should always be available")


def test_mock_search_does_not_raise() -> None:
    client = MockSearchClient()
    try:
        client.search("any query")
    except SearchError:
        raise AssertionError("mock should never raise SearchError")


def test_mock_search_query_preserved() -> None:
    client = MockSearchClient()
    response = client.search("specific query text")
    assert_equal(response.query, "specific query text", "query should be preserved in response")


# ── Factory ────────────────────────────────────────────────────────────────


def test_get_search_client_mock() -> None:
    client = get_search_client("mock")
    assert_true(isinstance(client, MockSearchClient), "mock provider returns MockSearchClient")


def test_get_search_client_invalid_raises() -> None:
    try:
        get_search_client("nonexistent_provider")
        raise AssertionError("should raise ValueError for unknown provider")
    except ValueError:
        pass


# ── SearchResponse and SearchResultItem ────────────────────────────────────


def test_search_result_item_defaults() -> None:
    item = SearchResultItem()
    assert_equal(item.title, "", "default title should be empty")
    assert_equal(item.url, "", "default url should be empty")
    assert_equal(item.source, "", "default source should be empty")


def test_search_response_query() -> None:
    results = [SearchResultItem(title="Test", url="https://example.com", snippet="s", source="mock")]
    response = SearchResponse(query="test", results=results, total_estimated=1, source="mock")
    assert_equal(response.query, "test", "response query should match")
    assert_equal(len(response.results), 1, "response should contain one result")


# ── Cache ──────────────────────────────────────────────────────────────────


def test_cache_miss_returns_none() -> None:
    search_cache.clear()
    result = search_cache.get("nonexistent query 12345", 5)
    assert_equal(result, None, "cache should return None on miss")


def test_cache_hit_after_set() -> None:
    search_cache.clear()
    query = "cache test query"
    response = SearchResponse(query=query, results=[], source="mock")
    search_cache.set(query, 5, response)

    cached = search_cache.get(query, 5)
    assert_true(cached is not None, "cache should hit after set")
    assert cached is not None
    assert_equal(cached.query, query, "cached response query should match")


def test_cache_key_is_normalised() -> None:
    search_cache.clear()
    query = "  Case Insensitive QUERY  "
    response = SearchResponse(query=query.strip(), results=[], source="mock")
    search_cache.set(query, 5, response)

    # Same query with different casing/whitespace should still hit
    cached = search_cache.get("case insensitive query", 5)
    assert_true(cached is not None, "cache should normalise query keys")
    assert cached is not None
    assert_equal(cached.query, query.strip(), "cached response should preserve original query")


def test_cache_different_max_results() -> None:
    search_cache.clear()
    query = "multi count"
    r5 = SearchResponse(query=query, results=[], source="mock")
    r10 = SearchResponse(query=query, results=[], source="mock")
    search_cache.set(query, 5, r5)
    search_cache.set(query, 10, r10)

    assert_true(search_cache.get(query, 5) is not None, "max_results=5 should hit")
    assert_true(search_cache.get(query, 10) is not None, "max_results=10 should hit")


def test_cache_clear() -> None:
    search_cache.clear()
    search_cache.set("k1", 5, SearchResponse(query="q1", results=[], source="mock"))
    search_cache.set("k2", 5, SearchResponse(query="q2", results=[], source="mock"))
    search_cache.clear()
    assert_equal(search_cache.get("k1", 5), None, "cache should be empty after clear")
    assert_equal(search_cache.get("k2", 5), None, "cache should be empty after clear")


# ── Run ────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    test_mock_search_returns_results()
    test_mock_search_respects_max_results()
    test_mock_search_available()
    test_mock_search_does_not_raise()
    test_mock_search_query_preserved()
    test_get_search_client_mock()
    test_get_search_client_invalid_raises()
    test_search_result_item_defaults()
    test_search_response_query()
    test_cache_miss_returns_none()
    test_cache_hit_after_set()
    test_cache_key_is_normalised()
    test_cache_different_max_results()
    test_cache_clear()
    print("PASS search_client_test")
