import json
import re
from html.parser import HTMLParser

import requests

_SEARCH_URL = "https://help.klaviyo.com/api/v2/help_center/articles/search.json"
_ARTICLE_URL = "https://help.klaviyo.com/api/v2/help_center/articles/{article_id}.json"
_HEADERS = {"User-Agent": "Klaviyo-Support-Agent/1.0", "Accept": "application/json"}
_TIMEOUT = 10

_STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of",
    "with", "is", "are", "was", "were", "be", "have", "has", "had", "do",
    "does", "did", "will", "would", "could", "should", "may", "might",
    "i", "my", "me", "we", "our", "you", "your", "it", "its",
    "this", "that", "what", "why", "how", "when", "where", "which",
    "not", "no", "s", "can", "please", "help", "tell",
}


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def get_text(self) -> str:
        text = " ".join(self._chunks)
        return re.sub(r"\s+", " ", text).strip()


def _strip_html(html: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(html)
    return stripper.get_text()


def _to_search_query(raw: str) -> str:
    """Convert a natural-language question to a compact keyword search query."""
    # Lower-case and remove punctuation except hyphens
    text = re.sub(r"[^\w\s\-]", " ", raw.lower())
    words = [w for w in text.split() if w and w not in _STOP_WORDS]
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique = [w for w in words if not (w in seen or seen.add(w))]  # type: ignore[func-returns-value]
    return " ".join(unique) if unique else raw


def _fetch_article_body(article_id: int) -> str:
    try:
        url = _ARTICLE_URL.format(article_id=article_id)
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
        body_html = resp.json().get("article", {}).get("body", "")
        return _strip_html(body_html)
    except Exception:
        return ""


def handle(input: dict) -> str:
    raw_query = input.get("query", "").strip()
    if not raw_query:
        return json.dumps({"error": "query is required"})

    search_query = _to_search_query(raw_query)

    try:
        resp = requests.get(
            _SEARCH_URL,
            params={"query": search_query, "locale": "en-us"},
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return json.dumps({"error": f"Knowledge base search failed: {e}"})

    raw_results = data.get("results", [])
    if not raw_results:
        return json.dumps({
            "search_query_used": search_query,
            "results": [],
            "message": "No articles found. Try rephrasing the question.",
        })

    articles = []
    for item in raw_results[:3]:
        article_id = item.get("id")
        body = _fetch_article_body(article_id) if article_id else ""
        # Fall back to snippet if full body fetch failed
        if not body:
            body = _strip_html(item.get("snippet", ""))
        articles.append({
            "id": article_id,
            "title": item.get("title", ""),
            "url": item.get("html_url", ""),
            "body": body,
        })

    return json.dumps({"search_query_used": search_query, "results": articles})
