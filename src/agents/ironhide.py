"""Ironhide — Designer Agent.

Translates research into concrete designs powered by the Open Design
ecosystem: 131 brand-grade design systems, 52 composable skills,
and a deterministic layout/token framework.

When designing, Ironhide:
1. Picks a design system (from 131 DESIGN.md specs)
2. Selects a skill pattern (web-prototype, dashboard, critique, etc.)
3. Uses the seed template + layout library
4. Applies the visual direction
5. Produces the design artifact
"""

from typing import Any, Dict, List, Optional
from src.agents import BaseAgent
from src.utils.opendesign import (
    list_design_systems,
    get_design_system,
    search_design_systems,
    list_skills,
    get_skill,
    get_skill_asset,
    get_web_prototype_seed,
    get_web_prototype_layouts,
    get_web_prototype_checklist,
    get_visual_directions,
    OD_FRAMES,
)


class Ironhide(BaseAgent):
    """Designer — turns research into production-quality designs using
    the Open Design ecosystem (131 design systems, 52 skills)."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Ironhide", config=config)
        self.designs: list = []
        self._design_system_cache: Dict[str, str] = {}

    def execute(self) -> Dict[str, Any]:
        """Produce design specifications using Open Design resources."""
        research = self.config.get("research", {})
        topic = research.get("topic", "default")
        deliverable_type = self.config.get("deliverable_type", "web_prototype")
        count = self.config.get("output_count", 3)

        # Pick a design system that matches the topic
        design_system = self._pick_design_system(topic)

        # Pick a skill pattern
        skill = self._pick_skill(deliverable_type)

        # Get the visual direction
        direction = self._pick_visual_direction(topic)

        # Generate designs
        self.designs = self._produce_designs(
            research=research,
            dtype=deliverable_type,
            count=count,
            design_system=design_system,
            skill=skill,
            direction=direction,
        )

        return {
            "deliverable_type": deliverable_type,
            "count": len(self.designs),
            "design_system_used": design_system.get("name", "none") if design_system else "none",
            "skill_used": skill.get("name", "none") if skill else "none",
            "visual_direction": direction.get("name", "none") if direction else "none",
            "designs": self.designs,
            "available_design_systems": len(list_design_systems()),
            "available_skills": len(list_skills()),
            "resources": self._get_resource_summary(),
        }

    def _pick_design_system(self, topic: str) -> Optional[Dict[str, str]]:
        """Find the best design system for this topic."""
        # Try search first
        matches = search_design_systems(topic)
        if matches:
            return matches[0]

        # Fallback: if no topic match, return a common default
        all_systems = list_design_systems()
        defaults = [
            s for s in all_systems
            if s["name"] in ("clean", "modern", "minimal", "claude")
        ]
        return defaults[0] if defaults else (all_systems[0] if all_systems else None)

    def _pick_skill(self, deliverable_type: str) -> Optional[Dict[str, str]]:
        """Find the best Open Design skill for this deliverable type."""
        all_skills = list_skills()

        # Map deliverable types to skill names
        type_map = {
            "web_prototype": "web-prototype",
            "landing_page": "saas-landing",
            "dashboard": "dashboard",
            "mobile_app": "mobile-app",
            "pricing_page": "pricing-page",
            "docs_page": "docs-page",
            "wireframe": "wireframe-sketch",
            "presentation": "guizang-ppt",
            "social_media": "social-carousel",
            "poster": "magazine-poster",
            "sprites": "sprite-animation",
            "kanban": "kanban-board",
            "critique": "critique",
        }

        skill_name = type_map.get(deliverable_type, "web-prototype")
        for s in all_skills:
            if s["name"] == skill_name:
                return s
        return all_skills[0] if all_skills else None

    def _pick_visual_direction(self, topic: str) -> Optional[Dict[str, str]]:
        """Pick a visual direction that fits the topic."""
        directions = get_visual_directions()
        if not directions:
            return None

        topic_lower = topic.lower()

        # Heuristic matching
        if any(w in topic_lower for w in ["tech", "developer", "code", "saas", "api"]):
            return directions[3]  # Tech Utility
        elif any(w in topic_lower for w in ["warm", "friendly", "soft", "creative"]):
            return directions[2]  # Warm Soft
        elif any(w in topic_lower for w in ["finance", "enterprise", "serious"]):
            return directions[1]  # Modern Minimal
        elif any(w in topic_lower for w in ["edgy", "artistic", "experimental", "bold"]):
            return directions[4]  # Brutalist Experimental
        else:
            return directions[0]  # Editorial Monocle (default)

    def _produce_designs(
        self,
        research: dict,
        dtype: str,
        count: int,
        design_system: Optional[Dict[str, str]],
        skill: Optional[Dict[str, str]],
        direction: Optional[Dict[str, str]],
    ) -> list:
        """Core design generation logic using Open Design methodology."""
        designs = []
        design_system_content = ""
        if design_system:
            design_system_content = get_design_system(design_system["name"]) or ""

        for i in range(count):
            design = {
                "name": f"{dtype}_{i + 1}",
                "description": f"{dtype.replace('_', ' ').title()} design #{i + 1}",
                "type": dtype,
                "design_system": design_system["name"] if design_system else "none",
                "skill": skill["name"] if skill else "none",
                "visual_direction": direction["name"] if direction else "none",
                "spec": {
                    "version": "1.0",
                    "status": "draft",
                    "informed_by": research.get("topic", "research"),
                    "approach": self._generate_approach(
                        dtype, design_system, skill, direction
                    ),
                },
            }

            # Add DESIGN.md preview if available
            if design_system_content:
                lines = design_system_content.split("\n")[:20]
                design["design_system_preview"] = "\n".join(lines)

            designs.append(design)

        return designs

    def _generate_approach(
        self,
        dtype: str,
        design_system: Optional[Dict[str, str]],
        skill: Optional[Dict[str, str]],
        direction: Optional[Dict[str, str]],
    ) -> str:
        """Generate an approach description for this design."""
        parts = ["Design approach:"]

        if design_system:
            parts.append(f"- Design System: {design_system['name']}")
            ds_content = get_design_system(design_system["name"]) or ""
            if ds_content:
                color_match = __import__("re").search(
                    r"Primary.*?(#[0-9A-Fa-f]{6})", ds_content
                )
                if color_match:
                    parts.append(f"- Primary color: {color_match.group(1)}")

        if skill:
            parts.append(f"- Skill pattern: {skill['name']} ({skill['scenario']})")

            # Load the skill's resources if available
            seed = get_web_prototype_seed()
            if seed:
                parts.append(f"- Seed template: loaded ({len(seed)} chars)")
            layouts = get_web_prototype_layouts()
            if layouts:
                parts.append(f"- Layout library: {len(layouts.split('#'))} sections available")
            checklist = get_web_prototype_checklist()
            if checklist:
                parts.append(f"- P0/P1/P2 checklist: loaded")

        if direction:
            parts.append(f"- Visual direction: {direction['name']}")
            parts.append(f"  {direction['description']}")
            parts.append(f"  Palette: {direction['palette']}")
            parts.append(f"  Fonts: {direction['font_stack']}")

        return "\n".join(parts)

    def _get_resource_summary(self) -> dict:
        """Return a summary of all available Open Design resources."""
        design_systems = list_design_systems()
        skills = list_skills()

        # Count by scenario
        scenario_counts = {}
        for s in skills:
            scenario = s.get("scenario", "other")
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

        return {
            "total_design_systems": len(design_systems),
            "total_skills": len(skills),
            "skills_by_scenario": scenario_counts,
            "design_system_names": [s["name"] for s in design_systems[:20]],
            "skill_names": [s["name"] for s in skills[:20]],
            "device_frames": list(OD_FRAMES.keys()),
            "visual_directions": [d["name"] for d in get_visual_directions()],
        }

    def suggest_skill(
        self, brief: str, platform: str = "desktop"
    ) -> List[Dict[str, str]]:
        """Suggest Open Design skills based on a project brief."""
        all_skills = list_skills()
        brief_lower = brief.lower()

        scoring = []
        for skill in all_skills:
            score = 0
            name = skill["name"]
            desc = skill["description"]

            # Score based on keywords
            triggers = {
                "landing|homepage|marketing": "saas-landing",
                "dashboard|admin|metrics": "dashboard",
                "mobile|app|phone": "mobile-app",
                "poster|magazine|editorial": "magazine-poster",
                "slide|presentation|pitch|deck": "guizang-ppt",
                "critique|review|audit": "critique",
                "wireframe|sketch|mockup": "wireframe-sketch",
                "pricing|plan|subscription": "pricing-page",
                "docs|documentation|guide": "docs-page",
                "kanban|board|trello": "kanban-board",
                "social|instagram|carousel": "social-carousel",
                "email|newsletter": "email-marketing",
                "blog|post|article": "blog-post",
                "animation|motion|sprite": "sprite-animation",
                "video|short|reel": "video-shortform",
                "invoice|receipt|billing": "invoice",
                "report|finance": "finance-report",
                "onboarding|hr": "hr-onboarding",
                "brief|spec|requirements": "design-brief",
            }

            for keywords, target in triggers.items():
                if target == name:
                    if any(k in brief_lower for k in keywords.split("|")):
                        score += 3

            # Default: web-prototype matches anything
            if name == "web-prototype":
                score += 1

            scoring.append({"name": name, "score": score, **skill})

        scoring.sort(key=lambda x: x["score"], reverse=True)
        return scoring[:5]