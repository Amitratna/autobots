"""OptimusPrime — Orchestrator Agent.

Receives the user's goal, decomposes it into tasks, delegates to
specialist agents, and synthesises results into a final deliverable.
"""

from typing import Any, Dict, List
from src.agents import BaseAgent


class OptimusPrime(BaseAgent):
    """The orchestrator — plans, delegates, and stitches results."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="OptimusPrime", config=config)
        self.agents: Dict[str, BaseAgent] = {}
        self.pipeline: List[str] = []
        self.results: Dict[str, Any] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Add a specialist agent to the workforce."""
        self.agents[agent.name] = agent
        self.pipeline.append(agent.name)

    def define_pipeline(self, ordered_names: List[str]) -> None:
        """Set a custom execution order."""
        for name in ordered_names:
            if name not in self.agents:
                raise ValueError(f"Unknown agent: {name}")
        self.pipeline = ordered_names

    def execute(self) -> Dict[str, Any]:
        """Run the full pipeline: delegate → collect → synthesise."""
        context: Dict[str, Any] = {"goal": self.config.get("goal", "")}

        for agent_name in self.pipeline:
            agent = self.agents[agent_name]
            self.send(
                recipient=agent,
                subject="execute",
                body=context,
            )
            result = agent.execute()
            self.results[agent_name] = result
            context[agent_name] = result

        return self._synthesise()

    def _synthesise(self) -> Dict[str, Any]:
        """Combine all agent outputs into a final deliverable."""
        return {
            "status": "complete",
            "pipeline": self.pipeline,
            "agent_results": self.results,
        }

    def __repr__(self) -> str:
        n = len(self.agents)
        return f"<OptimusPrime: {n} agent(s) registered>"