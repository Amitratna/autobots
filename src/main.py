"""AUTOBOTS — Main entry point.

Orchestrates the 7-agent pipeline to research, design, test, build,
market, and deploy digital illustration brushes.
"""

import json
import sys
from typing import Any, Dict

from src.agents.optimus_prime import OptimusPrime
from src.agents.bumblebee import Bumblebee
from src.agents.ironhide import Ironhide
from src.agents.ratchet import Ratchet
from src.agents.red_alert import RedAlert
from src.agents.jetfire import Jetfire
from src.agents.wheelie import Wheelie


def build_pipeline(config: Dict[str, Any]) -> OptimusPrime:
    """Construct and connect all 7 agents."""
    prime = OptimusPrime(config=config)

    bumblebee = Bumblebee(config=config.get("research", {}))
    ironhide = Ironhide(config=config.get("design", {}))
    ratchet = Ratchet(config=config.get("qa", {}))
    red_alert = RedAlert(config=config.get("development", {}))
    jetfire = Jetfire(config=config.get("deployment", {}))
    wheelie = Wheelie(config=config.get("marketing", {}))

    prime.register_agent(bumblebee)
    prime.register_agent(ironhide)
    prime.register_agent(ratchet)
    prime.register_agent(red_alert)
    prime.register_agent(jetfire)
    prime.register_agent(wheelie)

    return prime


def default_config() -> Dict[str, Any]:
    """Return a sensible default configuration for a brush run."""
    return {
        "goal": "Create and sell a set of 10 watercolour texture brushes for Procreate",
        "research": {
            "niche": "watercolour texture brushes",
            "platform": "etsy",
        },
        "design": {"brush_count": 10},
        "development": {"component": "dashboard"},
        "deployment": {"platforms": ["etsy", "gumroad"], "pack_size": 10},
        "marketing": {},
    }


def main() -> None:
    """Run the full AUTOBOTS pipeline."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    if config_path:
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = default_config()

    print(f"🤖 AUTOBOTS Pipeline Starting")
    print(f"   Goal: {config.get('goal', 'Untitled mission')}")
    print()

    prime = build_pipeline(config)
    result = prime.execute()

    print(f"\n✅ Pipeline Complete")
    print(f"   Agents run: {len(result.get('agent_results', {}))}")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()