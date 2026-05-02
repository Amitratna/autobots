"""RedAlert — Developer Agent.

Builds applications, websites, APIs, dashboards, and developer tooling.
Implements frontend, backend, and integration code.
"""

from typing import Any, Dict
from src.agents import BaseAgent


class RedAlert(BaseAgent):
    """Developer — builds production applications and tooling."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="RedAlert", config=config)
        self.artifacts: list = []

    def execute(self) -> Dict[str, Any]:
        """Build requested components and return output paths."""
        specs = self.config.get("specs", {})
        tech_stack = self.config.get("tech_stack", ["python", "html"])

        result = self._build(specs, tech_stack)

        return {
            "tech_stack": tech_stack,
            "artifacts": self.artifacts,
            **result,
        }

    def _build(self, specs: dict, stack: list) -> dict:
        """Core build logic — dispatches based on spec type."""
        project_type = specs.get("type", "web_app")

        if project_type == "web_app":
            return self._build_web_app(specs, stack)
        elif project_type == "api":
            return self._build_api(specs, stack)
        elif project_type == "cli_tool":
            return self._build_cli(specs, stack)
        else:
            return {"status": "unknown_type", "project_type": project_type}

    def _build_web_app(self, specs: dict, stack: list) -> dict:
        """Build a web application from specs."""
        name = specs.get("name", "app")
        self.artifacts.append(f"output/{name}/index.html")
        self.artifacts.append(f"output/{name}/app.js")
        return {
            "status": "built",
            "framework": stack[0] if stack else "static",
            "name": name,
        }

    def _build_api(self, specs: dict, stack: list) -> dict:
        """Build an API service from specs."""
        name = specs.get("name", "api")
        self.artifacts.append(f"output/{name}/server.py")
        return {"status": "built", "endpoints": specs.get("endpoints", [])}

    def _build_cli(self, specs: dict, stack: list) -> dict:
        """Build a CLI tool from specs."""
        name = specs.get("name", "tool")
        self.artifacts.append(f"output/{name}/cli.py")
        return {"status": "built", "entry_point": f"output/{name}/cli.py"}