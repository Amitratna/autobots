"""Ironhide — Designer Agent.

Translates research into concrete designs, specs, wireframes, or
prototypes. Works with any deliverable type — UI mockups, architecture
diagrams, data models, content outlines.
"""

from typing import Any, Dict
from src.agents import BaseAgent


class Ironhide(BaseAgent):
    """Designer — turns research into concrete designs and specs."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Ironhide", config=config)
        self.designs: list = []

    def execute(self) -> Dict[str, Any]:
        """Produce design specifications based on research data."""
        research = self.config.get("research", {})
        deliverable_type = self.config.get("deliverable_type", "spec")
        count = self.config.get("output_count", 3)

        self.designs = self._produce_designs(
            research=research,
            dtype=deliverable_type,
            count=count,
        )
        return {
            "deliverable_type": deliverable_type,
            "count": len(self.designs),
            "designs": self.designs,
        }

    def _produce_designs(
        self,
        research: dict,
        dtype: str,
        count: int,
    ) -> list:
        """Core design logic — override or extend for specific domains."""
        designs = []
        for i in range(count):
            designs.append({
                "name": f"{dtype}_{i + 1}",
                "description": f"{dtype.title()} design #{i + 1}",
                "type": dtype,
                "spec": {
                    "version": "1.0",
                    "status": "draft",
                    "informed_by": research.get("topic", "research"),
                },
            })
        return designs