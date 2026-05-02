"""Open Design integration — makes Open Design's design systems and skills
available to the AUTOBOTS workforce.

Open Design (https://github.com/nexu-io/open-design) is an open-source
design system framework with 52 skills and 131 DESIGN.md brand systems.
This module provides access to those resources for Ironhide and downstream agents.
"""

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path to the cloned Open Design repo
OD_PATH = Path("/data/data/com.termux/files/usr/tmp/open-design")
SKILLS_PATH = OD_PATH / "skills"
DESIGN_SYSTEMS_PATH = OD_PATH / "design-systems"
CRAFT_PATH = OD_PATH / "craft"
TEMPLATES_PATH = OD_PATH / "templates"
ASSETS_PATH = OD_PATH / "assets"


# ─── Design Systems ──────────────────────────────────────────────────

def list_design_systems() -> List[Dict[str, str]]:
    """List all available DESIGN.md brand systems from Open Design.

    Returns list of {name, path, description}.
    """
    if not DESIGN_SYSTEMS_PATH.exists():
        return []

    systems = []
    for entry in sorted(DESIGN_SYSTEMS_PATH.iterdir()):
        if entry.is_dir():
            design_md = entry / "DESIGN.md"
            if design_md.exists():
                description = _extract_frontmatter_desc(str(design_md))
                systems.append({
                    "name": entry.name,
                    "path": str(design_md),
                    "description": description,
                })
    return systems


def get_design_system(name: str) -> Optional[str]:
    """Get the full DESIGN.md content for a named design system.

    Falls back to fuzzy matching on name.
    """
    # Exact match
    path = DESIGN_SYSTEMS_PATH / name / "DESIGN.md"
    if path.exists():
        return path.read_text(encoding="utf-8")

    # Fuzzy: find the closest name match
    for entry in DESIGN_SYSTEMS_PATH.iterdir():
        if entry.is_dir() and name.lower() in entry.name.lower():
            p = entry / "DESIGN.md"
            if p.exists():
                return p.read_text(encoding="utf-8")

    # Search description
    for entry in DESIGN_SYSTEMS_PATH.iterdir():
        if entry.is_dir():
            p = entry / "DESIGN.md"
            if p.exists():
                desc = _extract_frontmatter_desc(str(p))
                if name.lower() in desc.lower():
                    return p.read_text(encoding="utf-8")

    return None


def search_design_systems(query: str) -> List[Dict[str, str]]:
    """Search design systems by name or description."""
    query = query.lower()
    results = []
    for entry in DESIGN_SYSTEMS_PATH.iterdir():
        if entry.is_dir():
            p = entry / "DESIGN.md"
            if p.exists():
                desc = _extract_frontmatter_desc(str(p))
                if query in entry.name.lower() or query in desc.lower():
                    results.append({
                        "name": entry.name,
                        "path": str(p),
                        "description": desc,
                    })
    return results


# ─── Skills ──────────────────────────────────────────────────────────

def list_skills() -> List[Dict[str, str]]:
    """List all available Open Design skills.

    Returns list of {name, description, mode, scenario}.
    """
    if not SKILLS_PATH.exists():
        return []

    skills = []
    for entry in sorted(SKILLS_PATH.iterdir()):
        if entry.is_dir():
            skill_md = entry / "SKILL.md"
            if skill_md.exists():
                info = _parse_skill_metadata(str(skill_md))
                skills.append(info)
    return skills


def get_skill(name: str) -> Optional[str]:
    """Get the full SKILL.md content for a named skill."""
    path = SKILLS_PATH / name / "SKILL.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def get_skill_asset(skill_name: str, asset_name: str) -> Optional[str]:
    """Read an asset file from a skill (e.g. template.html, reference)."""
    # Check assets/
    path = SKILLS_PATH / skill_name / "assets" / asset_name
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Check references/
    path = SKILLS_PATH / skill_name / "references" / asset_name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


# ─── Template / Seed ─────────────────────────────────────────────────

def get_web_prototype_seed() -> Optional[str]:
    """Get the web-prototype seed template (template.html).

    This is the foundation HTML used by Open Design's web-prototype skill.
    It contains the CSS class system, :root token variables, and HTML structure.
    """
    return get_skill_asset("web-prototype", "template.html")


def get_web_prototype_layouts() -> Optional[str]:
    """Get the web-prototype layouts library."""
    return get_skill_asset("web-prototype", "layouts.md")


def get_web_prototype_checklist() -> Optional[str]:
    """Get the web-prototype P0/P1/P2 checklist."""
    return get_skill_asset("web-prototype", "checklist.md")


# ─── Device frames ──────────────────────────────────────────────────

OD_FRAMES = {
    "iphone_15_pro": "assets/frames/iphone-15-pro.png",
    "pixel": "assets/frames/pixel.png",
    "ipad_pro": "assets/frames/ipad-pro.png",
    "macbook": "assets/frames/macbook.png",
    "browser_chrome": "assets/frames/browser-chrome.png",
}


# ─── Prompt / Direction system ──────────────────────────────────────

def get_visual_directions() -> List[Dict[str, str]]:
    """Get the 5 curated visual direction schools from Open Design.

    Returns list of {name, description, palette, font_stack}.
    """
    return [
        {
            "name": "Editorial Monocle",
            "description": "Magazine-inspired, high-contrast typography, generous whitespace, serif/display headlines",
            "palette": "OKLch — dark text on light surface, accent for CTAs only",
            "font_stack": "Playfair Display + Inter + JetBrains Mono",
        },
        {
            "name": "Modern Minimal",
            "description": "Clean, utilitarian, maximum content density, restrained color",
            "palette": "Monochromatic with 1 accent, OKLch",
            "font_stack": "Inter + system sans",
        },
        {
            "name": "Warm Soft",
            "description": "Friendly, approachable, rounded corners, soft shadows, warm tones",
            "palette": "Warm neutrals + pastel accent, OKLch",
            "font_stack": "system rounded + Inter",
        },
        {
            "name": "Tech Utility",
            "description": "Data-dense, dark-mode preference, monospace flourishes, developer-oriented",
            "palette": "Dark surface + bright accent, OKLch",
            "font_stack": "JetBrains Mono + Inter",
        },
        {
            "name": "Brutalist Experimental",
            "description": "Raw, asymmetrical, oversized type, unconventional layouts, high visual impact",
            "palette": "High-contrast limited palette, OKLch",
            "font_stack": "variable wght axes, mono or display",
        },
    ]


def get_design_system_section_requirements() -> List[str]:
    """Return the required sections for a valid DESIGN.md."""
    return [
        "visual-theme",
        "color-palette",
        "typography",
        "layout",
        "components",
        "motion",
        "voice",
        "dos-and-donts",
    ]


# ─── Helpers ─────────────────────────────────────────────────────────

def _extract_frontmatter_desc(filepath: str) -> str:
    """Extract the first line or tagline from a DESIGN.md file."""
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")[:500]
        # Read the first non-header line after ## heading
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith(">") and "Category" in stripped:
                continue
            if stripped.startswith(">") and len(stripped) > 5:
                return stripped[1:].strip()
        return "No description available"
    except Exception:
        return ""


_OD_SKILL_SCENARIOS = {
    "design": ["web-prototype", "saas-landing", "dashboard", "mobile-app",
               "gamified-app", "social-carousel", "magazine-poster",
               "dating-web", "sprite-animation", "wireframe-sketch"],
    "marketing": ["motion-frames", "email-marketing", "social-carousel",
                  "blog-post", "pricing-page", "image-poster",
                  "video-shortform", "digital-eguide", "hyperframes"],
    "product": ["pm-spec", "design-brief", "kanban-board", "tweaks",
                "critique"],
    "engineering": ["eng-runbook", "docs-page"],
    "operation": ["hr-onboarding", "meeting-notes", "team-okrs",
                  "weekly-update"],
    "finance": ["finance-report", "invoice"],
    "deck": ["guizang-ppt", "simple-deck", "replit-deck", "weekly-update"],
}


def _parse_skill_metadata(filepath: str) -> Dict[str, str]:
    """Parse OD skill frontmatter for name, description, mode, scenario."""
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")[:2000]
    except Exception:
        content = ""

    name = Path(filepath).parent.name
    description = ""

    # Extract description from YAML frontmatter
    m = re.search(r'description:\s*\|?\s*(.+?)(?:\n\S|\n---)', content, re.DOTALL)
    if m:
        description = m.group(1).strip().replace("\n  ", " ")[:150]
    else:
        m = re.search(r'description:\s*["\']?(.+?)["\']?\n', content)
        if m:
            description = m.group(1).strip()[:150]

    # Infer mode and scenario from frontmatter
    mode = "prototype"
    scenario = "design"
    m = re.search(r'mode:\s*(\S+)', content)
    if m:
        mode = m.group(1)
    m = re.search(r'scenario:\s*(\S+)', content)
    if m:
        scenario = m.group(1)

    # Scenario override from our map
    for s, skills in _OD_SKILL_SCENARIOS.items():
        if name in skills:
            scenario = s
            break

    return {
        "name": name,
        "description": description or "No description available",
        "mode": mode,
        "scenario": scenario,
    }