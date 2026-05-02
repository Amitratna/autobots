"""Ironhide — Designer Agent.

Translates research into real, production-quality HTML design files
using the Open Design ecosystem: 130+ DESIGN.md brand systems, 52 skills,
seed template, layout library, and P0/P1/P2 checklist.

Ironhide now generates actual .html files on disk, not just specs.
"""

from typing import Any, Dict, List, Optional
from src.agents import BaseAgent
from src.utils.opendesign import (
    list_design_systems,
    get_design_system,
    search_design_systems,
    list_skills,
    get_skill,
    get_web_prototype_seed,
    get_web_prototype_layouts,
    get_visual_directions,
    OD_FRAMES,
)
from src.utils.design_generator import (
    generate_page,
    generate_multi_page,
    extract_tokens,
)


class Ironhide(BaseAgent):
    """Designer — generates real HTML design files using Open Design."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Ironhide", config=config)
        self.designs: list = []

    def execute(self) -> Dict[str, Any]:
        """Produce actual design files on disk using Open Design resources."""
        research = self.config.get("research", {})
        topic = research.get("topic", "default")
        brand = self.config.get("brand", topic.split()[0].title() if topic else "Brand")
        page_type = self.config.get("page_type", "landing")

        # Pick design system & style direction
        design_system = self._pick_design_system(topic)
        ds_name = design_system["name"] if design_system else "clean"
        direction = self._pick_visual_direction(topic)

        # Generate a complete design as a real HTML file
        page_html, page_path = self._build_page(
            page_type=page_type,
            brand=brand,
            design_system_name=ds_name,
            topic=topic,
            direction=direction,
        )

        # Also generate a full multi-page set
        full_site = generate_multi_page(
            brand=brand,
            topic=topic,
            design_system=ds_name,
        )

        # Record resource usage
        all_ds = list_design_systems()
        all_skills = list_skills()

        result = {
            "deliverable_type": f"{page_type}_html",
            "count": len(full_site),
            "design_system_used": ds_name,
            "visual_direction": direction["name"] if direction else "default",
            "primary_page": {
                "type": page_type,
                "file_path": page_path,
                "html_size_bytes": len(page_html),
                "brand": brand,
                "topic": topic,
            },
            "generated_pages": full_site,
            "available_design_systems": len(all_ds),
            "available_skills": len(all_skills),
            "resources": {
                "seed_template_loaded": get_web_prototype_seed() is not None,
                "layouts_available": get_web_prototype_layouts() is not None,
                "design_system_sample": design_system,
            },
        }

        self.designs = [result]
        return result

    def generate_single_page(
        self,
        page_type: str = "landing",
        brand: str = "Brand",
        design_system: str = "clean",
        topic: str = "default",
    ) -> Dict[str, Any]:
        """Generate a single design page and return its metadata."""
        html, path = generate_page(
            page_type=page_type,
            brand_name=brand,
            design_system_name=design_system,
            topic=topic,
        )
        return {
            "page_type": page_type,
            "brand": brand,
            "design_system": design_system,
            "topic": topic,
            "file_path": path,
            "html_size": len(html),
            "status": "generated",
        }

    def _build_page(
        self,
        page_type: str,
        brand: str,
        design_system_name: str,
        topic: str,
        direction: Optional[Dict[str, str]],
    ) -> tuple:
        """Produce a real HTML page via the design generator."""
        # Auto-detect best page type if not specified
        topic_lower = topic.lower()
        if page_type == "auto":
            if any(w in topic_lower for w in ["saas", "app", "platform", "service"]):
                page_type = "saas_landing"
            elif any(w in topic_lower for w in ["pricing", "plan", "subscription"]):
                page_type = "pricing"
            elif any(w in topic_lower for w in ["about", "company", "team"]):
                page_type = "about"
            else:
                page_type = "landing"

        html, path = generate_page(
            page_type=page_type,
            brand_name=brand,
            design_system_name=design_system_name,
            topic=topic,
        )
        return html, path

    def _pick_design_system(self, topic: str) -> Optional[Dict[str, str]]:
        """Find the best design system for this topic."""
        matches = search_design_systems(topic)
        if matches:
            return matches[0]
        all_systems = list_design_systems()
        defaults = [
            s for s in all_systems
            if s["name"] in ("clean", "modern", "minimal", "claude", "agentic")
        ]
        return defaults[0] if defaults else (all_systems[0] if all_systems else None)

    def _pick_visual_direction(self, topic: str) -> Optional[Dict[str, str]]:
        """Pick a visual direction that fits the topic."""
        directions = get_visual_directions()
        if not directions:
            return None
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["tech", "developer", "code", "saas", "api"]):
            return directions[3]  # Tech Utility
        elif any(w in topic_lower for w in ["warm", "friendly", "soft", "creative"]):
            return directions[2]  # Warm Soft
        elif any(w in topic_lower for w in ["finance", "enterprise", "serious"]):
            return directions[1]  # Modern Minimal
        elif any(w in topic_lower for w in ["edgy", "artistic", "experimental", "bold"]):
            return directions[4]  # Brutalist Experimental
        else:
            return directions[0]  # Editorial Monocle