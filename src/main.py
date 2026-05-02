"""AUTOBOTS — Main entry point.

Orchestrates the 7-agent pipeline:
  Bumblebee (Research) → Ironhide (Design) → Ratchet (Analysis) →
  RedAlert (Dev) → Jetfire (Code) → Wheelie (QA)

Each agents receives the accumulated context from its predecessors,
so downstream agents always have full awareness of what came before.
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
    """Construct and connect all 7 agents in execution order."""
    prime = OptimusPrime(config=config)

    bumblebee = Bumblebee(config=config.get("research", {}))
    ironhide = Ironhide(config=config.get("design", {}))
    ratchet = Ratchet(config=config.get("analysis", {}))
    red_alert = RedAlert(config=config.get("development", {}))
    jetfire = Jetfire(config=config.get("coding", {}))
    wheelie = Wheelie(config=config.get("qa", {}))

    # Register in execution order
    prime.register_agent(bumblebee)
    prime.register_agent(ironhide)
    prime.register_agent(ratchet)
    prime.register_agent(red_alert)
    prime.register_agent(jetfire)
    prime.register_agent(wheelie)

    return prime


def default_config() -> Dict[str, Any]:
    """Return a sensible default configuration."""
    return {
        "goal": "Research, design, build, and ship a new product",
        "research": {
            "topic": "AI-assisted developer tools",
            "sources": ["web", "github"],
        },
        "design": {
            "deliverable_type": "spec",
            "output_count": 3,
        },
        "analysis": {
            "metrics": {"confidence": 0.8, "readiness": "analysis"},
        },
        "development": {
            "specs": {
                "type": "web_app",
                "name": "autobots-dashboard",
            },
            "tech_stack": ["python", "html"],
        },
        "coding": {
            "language": "python",
            "tasks": [
                {"name": "main", "module": "src"},
                {"name": "utils", "module": "src"},
            ],
            "designs": [],
        },
        "qa": {},
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
    print(f"   Pipeline: Bumblebee → Ironhide → Ratchet → RedAlert → Jetfire → Wheelie")
    print()

    prime = build_pipeline(config)
    result = prime.execute()

    # Pretty print the result summary
    agent_results = result.get("agent_results", {})
    print(f"\n✅ Pipeline Complete")
    print(f"   Agents executed: {len(agent_results)}")
    print()

    for agent_name, agent_result in agent_results.items():
        status = "✅" if isinstance(agent_result, dict) and agent_result.get("status") != "error" else "❌"
        print(f"   {status} {agent_name}: {list(agent_result.keys())[:3]}...")

    # Full JSON output to stderr so stdout can be piped cleanly
    print("\n" + json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()