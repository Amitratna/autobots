"""Ratchet — Tester / QA Agent.

Validates brush designs for quality, consistency, and completeness
before they go to deployment. Runs automated checks on design specs.
"""

from typing import Any, Dict, List
from src.agents import BaseAgent


class Ratchet(BaseAgent):
    """Quality assurance — ensures designs meet standards."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Ratchet", config=config)
        self.issues: List[str] = []

    def execute(self) -> Dict[str, Any]:
        """Run all quality checks on designs."""
        designs = self.config.get("designs", [])
        checks = {
            "naming": self._check_naming(designs),
            "parameters": self._check_parameters(designs),
            "completeness": self._check_completeness(designs),
        }
        passed = all(v.get("passed", False) for v in checks.values())
        return {
            "passed": passed,
            "checks": checks,
            "total_designs": len(designs),
            "issues": self.issues,
        }

    def _check_naming(self, designs: list) -> dict:
        """Ensure all designs have valid, unique names."""
        names = [d["name"] for d in designs if "name" in d]
        dupes = [n for n in names if names.count(n) > 1]
        if dupes:
            self.issues.append(f"Duplicate names: {set(dupes)}")
        return {
            "passed": len(dupes) == 0 and len(names) == len(designs),
            "total": len(names),
            "unique": len(set(names)),
        }

    def _check_parameters(self, designs: list) -> dict:
        """Verify all designs have required parameters."""
        required = {"size", "opacity", "texture"}
        missing = 0
        for d in designs:
            params = d.get("parameters", {})
            if not required.issubset(params.keys()):
                missing += 1
                self.issues.append(f"{d['name']}: missing params")
        return {"passed": missing == 0, "designs_with_issues": missing}

    def _check_completeness(self, designs: list) -> dict:
        """Check that every design has a name and description."""
        incomplete = [
            d["name"]
            for d in designs
            if not d.get("name") or not d.get("description")
        ]
        if incomplete:
            self.issues.append(f"Incomplete: {incomplete}")
        return {"passed": len(incomplete) == 0, "incomplete": incomplete}