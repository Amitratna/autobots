"""Wheelie — Marketing Agent.

Creates product titles, descriptions, tags, and promotional copy
for Etsy and Gumroad listings. Optimises for search and conversion.
"""

from typing import Any, Dict
from src.agents import BaseAgent


class Wheelie(BaseAgent):
    """Marketer — copywriting, SEO, and campaign generation."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Wheelie", config=config)
        self.campaigns: list = []

    def execute(self) -> Dict[str, Any]:
        """Generate marketing materials for all products."""
        packs = self.config.get("packs", [])
        research = self.config.get("research", {})
        keywords = research.get("keywords", [])

        for pack in packs:
            campaign = self._create_campaign(pack, keywords)
            self.campaigns.append(campaign)

        return {
            "campaigns": self.campaigns,
            "total_products": len(packs),
        }

    def _create_campaign(self, pack: dict, keywords: list) -> dict:
        """Generate title, description, tags, and social copy."""
        name = pack.get("name", "Brush Pack")
        count = pack.get("count", 10)
        kw_str = ", ".join(keywords[:5]) if keywords else "digital brushes"

        return {
            "product": name,
            "title": self._generate_title(name, count),
            "description": self._generate_description(name, count, kw_str),
            "tags": self._generate_tags(keywords),
            "social_copy": self._generate_social(name, count),
        }

    @staticmethod
    def _generate_title(name: str, count: int) -> str:
        return f"{count} Premium Digital Art Brushes – {name} for Procreate"

    @staticmethod
    def _generate_description(name: str, count: int, keywords: str) -> str:
        return (
            f"Elevate your digital art with this collection of {count} "
            f"hand-crafted {name.lower()}. Perfect for illustrators, "
            f"lettering artists, and designers.\n\n"
            f"Includes: {keywords}\n\n"
            f"Compatible with: Procreate, Photoshop, Affinity\n"
            f"File format: .brushset / .abr / .png stamps"
        )

    @staticmethod
    def _generate_tags(keywords: list) -> list:
        return (keywords[:10] if keywords
                else ["procreate", "brushes", "digital art"])

    @staticmethod
    def _generate_social(name: str, count: int) -> str:
        return (
            f"✨ Just created {count} new {name.lower()} — "
            f"perfect for your next digital illustration! 🎨 "
            f"Link in bio #digitalart #procreatebrushes"
        )