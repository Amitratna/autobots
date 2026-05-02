"""Bumblebee — Research Agent.

Gathers market intelligence, competitive data, trends, and domain-specific
research using real data sources: Wikipedia, DuckDuckGo, and Hacker News.
"""

from typing import Any, Dict
from src.agents import BaseAgent
from src.utils.sources import (
    research_topic,
    research_trends,
    wikipedia_search,
    duckduckgo_search,
    hackernews_search,
    fetch_page_text,
)


class Bumblebee(BaseAgent):
    """Researcher — gathers real market / domain intelligence from live sources."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Bumblebee", config=config)
        self.insights: Dict[str, Any] = {}
        self._errors: list = []

    def execute(self) -> Dict[str, Any]:
        """Analyse the domain using live data sources and return findings."""
        topic = self.config.get("topic", "current market")
        sources = self.config.get("sources", ["web", "trends"])
        audience = self.config.get("audience", "general")
        competitors = self.config.get("competitors", [])

        sources_used = []

        trends = self._analyse_trends()
        sources_used.extend(trends.get("_sources", []))

        comp = self._analyse_competition(competitors)
        sources_used.extend(comp.get("_sources", []))

        gaps = self._identify_gaps(topic)
        sources_used.extend(gaps.get("_sources", []))

        deep = self._deep_research(topic)
        sources_used.extend(deep.get("_sources", []))

        self.insights = {
            "topic": topic,
            "audience": audience,
            "sources_used": list(set(sources_used)),
            "trends": trends,
            "competitors": comp,
            "opportunities": gaps.get("insights", []),
            "deep_dive": deep,
            "errors": self._errors,
        }
        return self.insights

    def _analyse_trends(self) -> dict:
        """Fetch real trending data from Hacker News."""
        try:
            trends = research_trends()
            return {
                "source": "Hacker News top stories",
                "_sources": ["hacker_news"],
                "top_stories": trends.get("top_stories", []),
                "summary": trends.get("summary", ""),
            }
        except Exception as e:
            self._errors.append(f"Trend analysis failed: {e}")
            return {"source": "error", "_sources": [], "top_stories": [], "summary": str(e)}

    def _analyse_competition(self, competitors: list) -> dict:
        """Research each competitor using web/Wikipedia."""
        researched = []
        for name in competitors[:5]:
            try:
                results = wikipedia_search(name)
                ddg = duckduckgo_search(name)
                researched.append({
                    "name": name,
                    "wikipedia": results[:2] if results else [],
                    "duckduckgo_heading": ddg.get("heading", ""),
                    "duckduckgo_abstract": ddg.get("abstract", "")[:300],
                })
            except Exception as e:
                researched.append({"name": name, "error": str(e)})

        _sources = ["wikipedia", "duckduckgo"] if researched else []
        return {
            "top_players": [r["name"] for r in researched if "error" not in r],
            "market_position": self._estimate_position(researched),
            "_sources": _sources,
            "details": researched,
        }

    def _identify_gaps(self, topic: str) -> dict:
        """Use DuckDuckGo instant answers to identify market gaps."""
        try:
            ddg = duckduckgo_search(f"{topic} market gap opportunity")
            heading = ddg.get("heading", "")
            abstract = ddg.get("abstract", "")
            related = ddg.get("related_topics", [])[:3]

            insights = []
            if abstract:
                insights.append(abstract[:200])
            if heading:
                insights.append(f"Related topic: {heading}")
            for t in related:
                insights.append(f"Related: {t.get('text', '')[:100]}")
            if not insights:
                insights.append("No specific gaps identified from open sources")

            return {"insights": insights, "_sources": ["duckduckgo"]}
        except Exception as e:
            return {"insights": [f"Gap analysis unavailable: {e}"], "_sources": []}

    def _deep_research(self, topic: str) -> dict:
        """Run a comprehensive research sweep across all sources."""
        try:
            result = research_topic(topic)
            return {
                "_sources": ["wikipedia", "duckduckgo"],
                "wikipedia_articles": [
                    {"title": a["title"], "snippet": a["snippet"]}
                    for a in result.get("wikipedia", [])[:3]
                ],
                "wikipedia_summary": result.get("wikipedia_summary", "")[:1000],
                "instant_answer": result.get("instant_answer", {}).get("abstract", "")[:500],
                "related_topics": [
                    t.get("text", "")
                    for t in result.get("instant_answer", {}).get("related_topics", [])[:5]
                ],
            }
        except Exception as e:
            self._errors.append(f"Deep research failed: {e}")
            return {"_sources": []}

    @staticmethod
    def _estimate_position(competitors: list) -> str:
        """Rough estimate based on how much data we found."""
        known = sum(1 for c in competitors if "error" not in c)
        if known == 0:
            return "emerging — little competition data found"
        elif known <= 2:
            return "niche — few established players"
        else:
            return "competitive — multiple known players"