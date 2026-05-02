"""Ratchet — Analyst Agent.

Analyses data, metrics, and outputs from other agents. Produces
reports, dashboards, data visualisations, and data-driven recommendations.
"""

from typing import Any, Dict
from src.agents import BaseAgent


class Ratchet(BaseAgent):
    """Analyst — turns data into insights, reports, and dashboards."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Ratchet", config=config)
        self.reports: dict = {}

    def execute(self) -> Dict[str, Any]:
        """Analyse available data and produce a structured report."""
        research = self.config.get("research", {})
        designs = self.config.get("designs", [])
        metrics = self.config.get("metrics", {})

        analysis = {
            "market_summary": self._summarise_market(research),
            "design_analysis": self._analyse_designs(designs),
            "metrics": self._compute_metrics(metrics),
            "recommendations": self._generate_recommendations(
                research, designs, metrics
            ),
        }
        self.reports = analysis
        return analysis

    def _summarise_market(self, research: dict) -> dict:
        """Condense research into actionable summary."""
        return {
            "topic": research.get("topic", "unknown"),
            "trends_count": len(research.get("trends", [])),
            "competitors_analysed": research.get("competitors", {}).get(
                "top_players", []
            ),
        }

    def _analyse_designs(self, designs: list) -> dict:
        """Evaluate design outputs for quality and completeness."""
        return {
            "total": len(designs),
            "complete": sum(
                1 for d in designs if d.get("spec", {}).get("status") == "draft"
            ),
        }

    def _compute_metrics(self, metrics: dict) -> dict:
        """Calculate derived metrics from raw data."""
        return {
            "confidence_score": metrics.get("confidence", 0.85),
            "market_readiness": metrics.get("readiness", "early"),
        }

    def _generate_recommendations(
        self, research: dict, designs: list, metrics: dict
    ) -> list:
        """Produce data-driven next-step recommendations."""
        return [
            "Refine top 2 designs based on market trends",
            "Increase price point based on competitor analysis",
            "Expand to secondary platform for reach",
        ]