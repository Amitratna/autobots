"""HTML design generator — produces production-quality HTML files using
Open Design's seed template, layout library, and DESIGN.md tokens.

Ironhide uses this to generate real design artifacts instead of specs.
"""

import re
import html as html_mod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.utils.opendesign import (
    get_design_system,
    get_web_prototype_seed,
    get_web_prototype_layouts,
    search_design_systems,
    list_design_systems,
)
from src.utils.sources import research_topic as fetch_research


OUTPUT_DIR = Path.home() / "autobots" / "output" / "designs"


# ─── DESIGN.md token extraction ──────────────────────────────────────

def extract_tokens(design_system_name: str) -> Dict[str, str]:
    """Extract CSS token values from a DESIGN.md brand spec.

    Returns a dict mapping template :root variables to values.
    """
    tokens = {
        "--bg": "#fafaf7",
        "--surface": "#ffffff",
        "--fg": "#1a1916",
        "--muted": "#6b6964",
        "--border": "#e8e5df",
        "--accent": "#c96442",
    }

    content = get_design_system(design_system_name)
    if not content:
        return tokens

    # Color extraction patterns — DESIGN.md typically lists:
    # - **Primary:** `#FF5701`
    # - **Background:** `#0D1117`
    color_map = {
        "primary": "--accent",
        "secondary": "--accent",  # fallback
        "surface": "--surface",
        "background": "--bg",
        "bg": "--bg",
        "text": "--fg",
        "neutral": "--border",
        "muted": "--muted",
        "border": "--border",
    }

    for label, var in color_map.items():
        # Match: **Label:** `#HEX` or **Label:** #HEX or Label: #HEX
        patterns = [
            rf'\*\*{label}\*\*:\s*`?(#[0-9A-Fa-f]{{6}})`?',
            rf'\*\*{label}\*\*:\s*(#[0-9A-Fa-f]{{6}})',
            rf'{label}:\s*`?(#[0-9A-Fa-f]{{6}})`?',
        ]
        for pat in patterns:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                tokens[var] = m.group(1)
                break

    # Typography extraction
    font_matches = re.findall(
        r'\*\*Families:\*\*\s*(.+?)(?:\n|$)',
        content, re.IGNORECASE
    )
    if font_matches:
        fonts = font_matches[0]
        if "mono" in fonts.lower():
            m = re.search(r'mono=([\w\s-]+)', fonts)
            if m:
                tokens["--font-mono"] = m.group(1).strip()
        if "primary" in fonts.lower() or "display" in fonts.lower():
            m = re.search(r'(?:primary|display)=([\w\s,\'-]+)', fonts)
            if m:
                font = m.group(1).strip()
                tokens["--font-display"] = f"'{font}', serif"

    return tokens


# ─── Section builder ─────────────────────────────────────────────────

def _build_hero_center(
    headline: str, subhead: str, eyebrow: str,
    cta_primary: str, cta_secondary: str
) -> str:
    return f'''<section class="section hero" data-od-id="hero">
  <div class="container hero-center">
    <p class="eyebrow">{html_mod.escape(eyebrow)}</p>
    <h1>{html_mod.escape(headline)}</h1>
    <p class="lead">{html_mod.escape(subhead)}</p>
    <div class="hero-cta">
      <button class="btn btn-primary">{html_mod.escape(cta_primary)}</button>
      <button class="btn btn-secondary">{html_mod.escape(cta_secondary)}</button>
    </div>
  </div>
</section>'''


def _build_hero_split(
    headline: str, subhead: str, eyebrow: str,
    cta_primary: str, cta_secondary: str,
    visual_label: str = "Product visual"
) -> str:
    return f'''<section class="section" data-od-id="hero-split">
  <div class="container hero-split">
    <div>
      <p class="eyebrow">{html_mod.escape(eyebrow)}</p>
      <h1>{html_mod.escape(headline)}</h1>
      <p class="lead" style="margin-top: 20px;">{html_mod.escape(subhead)}</p>
      <div class="hero-cta" style="margin-top: 28px;">
        <button class="btn btn-primary">{html_mod.escape(cta_primary)}</button>
        <button class="btn btn-ghost btn-arrow">{html_mod.escape(cta_secondary)}</button>
      </div>
    </div>
    <div class="ph-img wide" aria-label="Hero visual placeholder">[ {html_mod.escape(visual_label)} · 16:9 ]</div>
  </div>
</section>'''


def _build_features(
    eyebrow: str, heading: str,
    features: List[Dict[str, str]]
) -> str:
    items = []
    for f in features[:6]:
        items.append(f'''      <div class="feature card-flat">
        <div class="feature-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="{f.get('icon_path', 'M12 3v18M3 12h18')}"/></svg>
        </div>
        <h3>{html_mod.escape(f.get('title', 'Feature'))}</h3>
        <p>{html_mod.escape(f.get('description', ''))}</p>
      </div>''')

    cols = min(len(items), 4)
    grid_class = f"grid-{max(cols, 2)}"

    return f'''<section class="section" data-od-id="features">
  <div class="container stack" style="gap: 56px;">
    <div style="max-width: 36ch;">
      <p class="eyebrow">{html_mod.escape(eyebrow)}</p>
      <h2>{html_mod.escape(heading)}</h2>
    </div>
    <div class="{grid_class}">
{chr(10).join(items)}
    </div>
  </div>
</section>'''


def _build_stats(stats: List[Dict[str, str]]) -> str:
    items = []
    for s in stats[:3]:
        items.append(f'''      <div class="stat">
        <div class="stat-num num"><span class="stat-unit">{html_mod.escape(s.get('num', '99'))}</span></div>
        <p class="stat-label">{html_mod.escape(s.get('label', ''))}</p>
      </div>''')

    return f'''<section class="section" data-od-id="stats">
  <div class="container">
    <p class="eyebrow" style="margin-bottom: 40px;">BY THE NUMBERS · {'2026'}</p>
    <div class="grid-3">
{chr(10).join(items)}
    </div>
  </div>
</section>'''


def _build_cta(heading: str, subtext: str, button_text: str) -> str:
    return f'''<section class="section" data-od-id="cta-strip" style="text-align: center;">
  <div class="container" style="max-width: 600px;">
    <h2>{html_mod.escape(heading)}</h2>
    <p class="lead" style="margin: 16px auto 32px;">{html_mod.escape(subtext)}</p>
    <button class="btn btn-primary">{html_mod.escape(button_text)}</button>
  </div>
</section>'''


def _build_log_list(items: List[Dict[str, str]]) -> str:
    entries = []
    for item in items[:8]:
        entries.append(f'''      <article class="log-row">
        <span class="meta">{html_mod.escape(item.get('date', ''))}</span>
        <div>
          <h3>{html_mod.escape(item.get('title', ''))}</h3>
          <p style="margin: 4px 0 0; color: var(--muted); font-size: 14px;">{html_mod.escape(item.get('summary', ''))}</p>
        </div>
        <span class="pull meta">{html_mod.escape(item.get('tag', ''))}</span>
      </article>''')

    return f'''<section class="section" data-od-id="log">
  <div class="container">
    <div class="row-between" style="margin-bottom: 32px;">
      <h2>Latest</h2>
      <a class="btn btn-ghost btn-arrow" href="#">View all</a>
    </div>
    <div>
{chr(10).join(entries)}
    </div>
  </div>
</section>'''


def _build_pricing_table(heading: str, plans: List[Dict[str, Any]]) -> str:
    if not plans:
        return ""

    # Header row
    headers = ["Plan"] + [p.get("name", "Plan") for p in plans]
    header_cells = "".join(f"<th>{h}</th>" for h in headers)

    # Feature rows
    features = plans[0].get("features", []) if plans else []
    body_rows = []
    for feat_name in features:
        cells = f"<td>{feat_name}</td>"
        for plan in plans:
            has = plan.get("features", {}).get(feat_name, "—")
            cells += f"<td>{has}</td>"
        body_rows.append(f"<tr>{cells}</tr>")

    return f'''<section class="section" data-od-id="pricing">
  <div class="container">
    <h2 style="margin-bottom: 40px;">{html_mod.escape(heading)}</h2>
    <table class="ds-table">
      <thead><tr>{header_cells}</tr></thead>
      <tbody>{chr(10).join(body_rows)}</tbody>
    </table>
  </div>
</section>'''


# ─── Full page generator ─────────────────────────────────────────────

PAGE_CONFIGS = {
    "landing": {
        "sections": ["hero_center", "features", "stats", "cta"],
        "description": "Primary landing/marketing page",
    },
    "saas_landing": {
        "sections": ["hero_split", "features", "stats", "pricing", "cta"],
        "description": "SaaS product landing with pricing",
    },
    "product_page": {
        "sections": ["hero_center", "features", "log_list", "cta"],
        "description": "Product detail with changelog/blog",
    },
    "pricing": {
        "sections": ["hero_center", "pricing", "cta"],
        "description": "Pricing and plans page",
    },
    "about": {
        "sections": ["hero_center", "stats", "log_list", "cta"],
        "description": "About / company page",
    },
}


def generate_page(
    page_type: str,
    brand_name: str,
    design_system_name: str,
    topic: str,
    year: str = "2026",
    custom_sections: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """Generate a complete HTML page using Open Design methodology.

    Returns (html_content, file_path).
    """
    tokens = extract_tokens(design_system_name)
    seed = get_web_prototype_seed()
    if not seed:
        raise ValueError("Open Design seed template not found")

    # Determine section order
    page_config = PAGE_CONFIGS.get(page_type, PAGE_CONFIGS["landing"])
    section_order = custom_sections or page_config["sections"]

    # Build content for each section
    topic_words = topic.split()
    brand_display = brand_name or (topic_words[0].title() if topic_words else "Brand")

    sections_html = []
    for sec in section_order:
        if sec == "hero_center":
            sections_html.append(_build_hero_center(
                headline=f"Learn {topic.title()}",
                subhead=f"Master {topic} through interactive lessons and hands-on exercises",
                eyebrow="START LEARNING",
                cta_primary="Get Started Free",
                cta_secondary="Browse Lessons",
            ))
        elif sec == "hero_split":
            sections_html.append(_build_hero_split(
                headline=f"The Best Way to Learn {topic.title()}",
                subhead=f"Interactive CLI tools + web dashboard — learn by doing, not by watching",
                eyebrow="EDUCATION REIMAGINED",
                cta_primary="Start Learning",
                cta_secondary="See How It Works",
                visual_label=f"{topic} platform demo",
            ))
        elif sec == "features":
            sections_html.append(_build_features(
                eyebrow="WHAT YOU GET",
                heading=f"Everything you need to master {topic}",
                features=[
                    {"title": "Interactive Lessons", "description": f"Learn {topic} with step-by-step guides, real examples, and built-in quizzes that reinforce every concept.", "icon_path": "M12 3v18M3 12h18"},
                    {"title": "Hands-On CLI", "description": "Practice directly from your terminal. No setup, no config — just type and learn.", "icon_path": "M4 7h16M4 12h10M4 17h16"},
                    {"title": "Progress Tracking", "description": "Pick up where you left off. Your progress syncs between CLI and web dashboard automatically.", "icon_path": "M12 8v4l3 2"},
                    {"title": "Agent Playground", "description": "Experiment with AI agents in a safe sandbox. See how they think, reason, and act in real time.", "icon_path": "M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0"},
                ],
            ))
        elif sec == "stats":
            sections_html.append(_build_stats([
                {"num": "6+", "label": f"In-depth {topic} lessons — from basics to advanced"},
                {"num": "24+", "label": "Interactive quiz questions to test your knowledge"},
                {"num": "100%", "label": "Free and open-source — learn at your own pace"},
            ]))
        elif sec == "cta":
            sections_html.append(_build_cta(
                heading=f"Start learning {topic} today",
                subtext="Free. No account required. Just you and your terminal.",
                button_text="Get Started →",
            ))
        elif sec == "log_list":
            sections_html.append(_build_log_list([
                {"date": "Today", "title": f"New: {topic} Lesson 6", "summary": "Building your first agent — practical walkthrough with real code.", "tag": "New"},
                {"date": "Yesterday", "title": f"Updated: {topic} Lesson 3", "summary": "Expanded tools & function calling with more examples.", "tag": "Updated"},
                {"date": "This week", "title": "Agent Playground launched", "summary": "Experiment with simulated agents directly in your browser.", "tag": "Feature"},
            ]))
        elif sec == "pricing":
            sections_html.append(_build_pricing_table(
                heading="Simple, transparent pricing",
                plans=[
                    {"name": "Free", "features": {"All lessons": "✓", "CLI access": "✓", "Web dashboard": "✓", "Progress sync": "✓", "Agent playground": "✓", "Community support": "✓", "Priority support": "—", "Custom lessons": "—"}, "price": "$0"},
                    {"name": "Pro", "features": {"All lessons": "✓", "CLI access": "✓", "Web dashboard": "✓", "Progress sync": "✓", "Agent playground": "✓", "Community support": "✓", "Priority support": "✓", "Custom lessons": "—"}, "price": "$9/mo"},
                    {"name": "Enterprise", "features": {"All lessons": "✓", "CLI access": "✓", "Web dashboard": "✓", "Progress sync": "✓", "Agent playground": "✓", "Community support": "✓", "Priority support": "✓", "Custom lessons": "✓"}, "price": "Custom"},
                ],
            ))

    sections_block = "\n\n".join(sections_html)

    # Inject into seed template
    page = seed.replace("[REPLACE] Page title · brand", f"{brand_display} · {topic}")
    page = page.replace("[REPLACE] Brand", brand_display)
    page = page.replace("[REPLACE] Link 1", "Learn")
    page = page.replace("[REPLACE] Link 2", "Playground")
    page = page.replace("[REPLACE] Link 3", "About")
    page = page.replace("[REPLACE] CTA", "Get Started")
    page = page.replace("© [REPLACE] Brand · [REPLACE] Year", f"© {brand_display} · {year}")
    page = page.replace("[REPLACE] tagline · contact@example.com", f"learn {topic.lower()} · hello@{brand_display.lower().replace(' ', '')}.com")

    # Inject design system tokens — replace the :root variable declarations
    root_start = page.find(":root {")
    root_end = page.find("}", root_start) + 1 if root_start != -1 else -1

    if root_start != -1 and root_end != -1:
        old_root = page[root_start:root_end]
        new_root_lines = ["    :root {"]
        for var, val in tokens.items():
            new_root_lines.append(f"      {var}:  {val};")
        # Copy remaining template root vars
        for line in old_root.split("\n"):
            stripped = line.strip()
            if stripped.startswith("--") and not any(
                stripped.startswith(k) for k in tokens
            ):
                new_root_lines.append(line)
        new_root_lines.append("    }")
        new_root = "\n".join(new_root_lines)
        page = page[:root_start] + new_root + page[root_end:]

    # Inject all sections into <main> — replace the placeholder hero section
    # Find the hero section placeholder and replace it with our full section block
    hero_pattern = r'<section class="section hero".*?</section>'
    sections_first = sections_block.split("\n\n")[0] if sections_block else ""
    page = re.sub(hero_pattern, sections_first, page, count=1, flags=re.DOTALL)

    # Now inject remaining sections before the </main> tag
    remaining_sections = "\n\n".join(sections_block.split("\n\n")[1:])
    page = page.replace("</main>", remaining_sections + "\n  </main>")

    # Write file
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', brand_domain := brand_name.lower().replace(' ', '-'))[:40]
    filename = f"{safe_name}-{page_type}.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    filepath.write_text(page, encoding="utf-8")

    return page, str(filepath)


def generate_page_from_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a design page from a pipeline config dict.

    Returns metadata about the generated page.
    """
    topic = config.get("research", {}).get("topic", "AI Agents")
    design_system = config.get("design_system", "modern")
    brand = config.get("brand", topic.split()[0].title() if topic else "AI Academy")
    page_type = config.get("page_type", "landing")

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
        "html_length": len(html),
        "file_path": path,
        "status": "generated",
    }


def generate_multi_page(brand: str, topic: str, design_system: str = "agentic") -> List[Dict[str, Any]]:
    """Generate a full set of pages for a project."""
    results = []
    for page_type in ["landing", "saas_landing", "pricing", "about"]:
        try:
            html, path = generate_page(
                page_type=page_type,
                brand_name=brand,
                design_system_name=design_system,
                topic=topic,
            )
            results.append({
                "page_type": page_type,
                "file_path": path,
                "size_bytes": len(html),
                "status": "generated",
            })
        except Exception as e:
            results.append({
                "page_type": page_type,
                "status": "error",
                "error": str(e),
            })
    return results