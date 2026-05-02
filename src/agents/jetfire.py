"""Jetfire — Deployment Agent.

Packages brush files and assets, generates listing metadata,
and deploys to Etsy and Gumroad via their APIs.
"""

from typing import Any, Dict
from src.agents import BaseAgent


class Jetfire(BaseAgent):
    """Deployment — packages and ships to marketplaces."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Jetfire", config=config)
        self.deployments: list = []

    def execute(self) -> Dict[str, Any]:
        """Prepare and deploy listings to target platforms."""
        designs = self.config.get("designs", [])
        platforms = self.config.get("platforms", ["etsy", "gumroad"])

        for platform in platforms:
            result = self._deploy_to(platform, designs)
            self.deployments.append(result)

        return {
            "deployments": self.deployments,
            "total_listings": sum(
                d.get("listings_created", 0) for d in self.deployments
            ),
        }

    def _deploy_to(self, platform: str, designs: list) -> dict:
        """Prepare and dispatch a listing for one platform."""
        # Stub — Phase 4 replaces with actual API calls
        packs = self._bundle_into_packs(designs)
        return {
            "platform": platform,
            "packs_created": len(packs),
            "listings_created": len(packs),
            "status": "prepared",
        }

    def _bundle_into_packs(self, designs: list) -> list:
        """Group designs into sellable packs."""
        pack_size = self.config.get("pack_size", 10)
        packs = []
        for i in range(0, len(designs), pack_size):
            chunk = designs[i : i + pack_size]
            packs.append({
                "name": f"Brush Pack {i // pack_size + 1}",
                "count": len(chunk),
                "designs": [d["name"] for d in chunk],
                "price": self._suggest_price(len(chunk)),
            })
        return packs

    @staticmethod
    def _suggest_price(count: int) -> str:
        if count <= 5:
            return "$3.99"
        elif count <= 20:
            return "$9.99"
        else:
            return "$19.99"