"""Real data sources for Bumblebee and downstream agents.

Uses free, no-API-key-required data sources: Wikipedia, DuckDuckGo,
Hacker News, and configurable RSS feeds.
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


# ─── Helpers ──────────────────────────────────────────────────────────

def _fetch_json(url: str, timeout: int = 8) -> dict:
    """Fetch a URL and parse JSON response."""
    req = urllib.request.Request(url, headers={"User-Agent": "AUTOBOTS/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def _fetch_text(url: str, timeout: int = 8) -> str:
    """Fetch a URL and return raw text."""
    req = urllib.request.Request(url, headers={"User-Agent": "AUTOBOTS/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode()
    except Exception:
        return ""


# ─── Wikipedia ────────────────────────────────────────────────────────

WIKI_API = "https://en.wikipedia.org/w/api.php"


def wikipedia_search(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Search Wikipedia for articles matching a query.

    Returns list of {title, url, snippet}.
    """
    params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
        "srprop": "snippet",
    })
    url = f"{WIKI_API}?{params}"
    data = _fetch_json(url)

    results = []
    for item in data.get("query", {}).get("search", []):
        results.append({
            "title": item["title"],
            "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item['title'].replace(' ', '_'))}",
            "snippet": re.sub(r"<[^>]+>", "", item.get("snippet", "")),
        })
    return results


def wikipedia_summary(title: str) -> Optional[str]:
    """Get the plain-text summary of a Wikipedia article."""
    params = urllib.parse.urlencode({
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": title,
        "format": "json",
    })
    url = f"{WIKI_API}?{params}"
    data = _fetch_json(url)

    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id != "-1":
            return page.get("extract", "")
    return None


# ─── DuckDuckGo Instant Answer API ────────────────────────────────────

DDG_API = "https://api.duckduckgo.com/"


def duckduckgo_search(query: str) -> Dict[str, Any]:
    """Get instant answers, related topics, and abstract from DuckDuckGo.

    Returns structured results with abstract, source, and related topics.
    """
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    })
    url = f"{DDG_API}?{params}"
    data = _fetch_json(url)

    results = {
        "abstract": data.get("AbstractText", ""),
        "abstract_source": data.get("AbstractSource", ""),
        "abstract_url": data.get("AbstractURL", ""),
        "answer": data.get("Answer", ""),
        "answer_type": data.get("AnswerType", ""),
        "heading": data.get("Heading", ""),
        "image": data.get("Image", ""),
        "related_topics": [],
    }

    for topic in data.get("RelatedTopics", []):
        if "Topics" in topic:
            for sub in topic["Topics"]:
                results["related_topics"].append({
                    "text": sub.get("Text", ""),
                    "url": sub.get("FirstURL", ""),
                })
        else:
            results["related_topics"].append({
                "text": topic.get("Text", ""),
                "url": topic.get("FirstURL", ""),
            })

    return results


# ─── Hacker News ─────────────────────────────────────────────────────

HN_API = "https://hacker-news.firebaseio.com/v0"


def hackernews_top_stories(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top stories from Hacker News.

    Returns list of {title, url, score, by, descendants}.
    """
    story_ids = _fetch_json(f"{HN_API}/topstories.json")[:limit]
    stories = []
    for sid in story_ids:
        item = _fetch_json(f"{HN_API}/item/{sid}.json")
        if item and item.get("type") == "story":
            stories.append({
                "title": item.get("title", ""),
                "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                "score": item.get("score", 0),
                "by": item.get("by", ""),
                "comments": item.get("descendants", 0),
            })
    return stories


def hackernews_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search Hacker News stories using Algolia-powered HN Search.

    Returns list of {title, url, points, author, created_at}.
    """
    params = urllib.parse.urlencode({
        "query": query,
        "tags": "story",
        "hitsPerPage": limit,
    })
    url = f"https://hn.algolia.com/api/v1/search?{params}"
    data = _fetch_json(url)

    results = []
    for hit in data.get("hits", []):
        results.append({
            "title": hit.get("title", ""),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
            "points": hit.get("points", 0),
            "author": hit.get("author", ""),
            "created_at": hit.get("created_at", ""),
        })
    return results


# ─── Web page scraper (lightweight) ───────────────────────────────────

def fetch_page_text(url: str, max_chars: int = 5000) -> str:
    """Fetch a web page and extract readable text content.

    Strips HTML tags, normalises whitespace, truncates to max_chars.
    """
    try:
        html = _fetch_text(url, timeout=8)
        # Strip tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Decode HTML entities
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&quot;", '"').replace("&#39;", "'")
        # Normalise whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception as e:
        return f"[Error fetching page: {e}]"


# ─── Combined search ──────────────────────────────────────────────────

def research_topic(topic: str) -> Dict[str, Any]:
    """Run a full research sweep across all available sources.

    Returns a consolidated dict with results from Wikipedia, DuckDuckGo,
    and Hacker News.
    """
    results = {
        "topic": topic,
        "wikipedia": wikipedia_search(topic),
        "instant_answer": duckduckgo_search(topic),
        "hacker_news": hackernews_search(topic),
    }

    # Enrich with Wikipedia summary if we found a match
    if results["wikipedia"]:
        summary = wikipedia_summary(results["wikipedia"][0]["title"])
        if summary:
            results["wikipedia_summary"] = summary[:2000]

    return results


def research_trends() -> Dict[str, Any]:
    """Gather trending/current topics.

    Returns Hacker News top stories, which serve as a proxy for
    current tech/business trends.
    """
    top_stories = hackernews_top_stories(15)
    return {
        "source": "Hacker News",
        "top_stories": top_stories,
        "summary": "Top stories from Hacker News — good proxy for tech/startup trends.",
    }