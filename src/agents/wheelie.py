"""Wheelie — Quality Inspector Agent.

Reviews all outputs from the pipeline — design specs, code, copy,
data — for quality, consistency, correctness, and completeness.
The last line of defence before shipping.
"""

from typing import Any, Dict, List
from src.agents import BaseAgent


class Wheelie(BaseAgent):
    """Quality Inspector — validates everything before it ships."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Wheelie", config=config)
        self.issues: List[str] = []
        self.review_log: List[dict] = []

    def execute(self) -> Dict[str, Any]:
        """Run all quality checks across the pipeline outputs."""
        research = self.config.get("research", {})
        designs = self.config.get("designs", [])
        code_artifacts = self.config.get("code_artifacts", [])
        analysis = self.config.get("analysis", {})

        checks = {
            "research_quality": self._check_research(research),
            "design_quality": self._check_designs(designs),
            "code_quality": self._check_code(code_artifacts),
            "analysis_quality": self._check_analysis(analysis),
            "consistency": self._check_global_consistency(
                research, designs, code_artifacts
            ),
        }

        passed = all(v.get("passed", False) for v in checks.values())
        return {
            "passed": passed,
            "checks": checks,
            "total_issues": len(self.issues),
            "issues": self.issues,
            "review_log": self.review_log,
        }

    def _check_research(self, research: dict) -> dict:
        """Validate research outputs."""
        issues = []
        if not research.get("trends"):
            issues.append("No trends identified")
        if not research.get("competitors"):
            issues.append("No competitor analysis")
        self.issues.extend(issues)
        return {"passed": len(issues) == 0, "issues": issues}

    def _check_designs(self, designs: list) -> dict:
        """Validate design outputs for required fields."""
        if not designs:
            self.issues.append("No designs produced")
            return {"passed": False, "issues": ["No designs"]}

        missing_fields = 0
        for d in designs:
            if not d.get("name"):
                missing_fields += 1
                self.issues.append("Design missing name")
            if not d.get("spec"):
                missing_fields += 1
                self.issues.append("Design missing spec")

        return {
            "passed": missing_fields == 0,
            "total": len(designs),
            "issues_count": missing_fields,
        }

    def _check_code(self, artifacts: list) -> dict:
        """Validate code artifacts were produced."""
        if not artifacts:
            self.issues.append("No code artifacts produced")
            return {"passed": False, "issues": ["No code artifacts"]}

        self.review_log.append(
            f"Reviewed {len(artifacts)} code artifacts"
        )
        return {
            "passed": True,
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
        }

    def _check_analysis(self, analysis: dict) -> dict:
        """Validate analysis outputs."""
        if not analysis.get("recommendations"):
            self.issues.append("No recommendations produced")
            return {"passed": False, "issues": ["Missing recommendations"]}
        return {"passed": True, "recommendations": len(analysis["recommendations"])}

    def _check_global_consistency(
        self,
        research: dict,
        designs: list,
        code_artifacts: list,
    ) -> dict:
        """Cross-check that all outputs are consistent with each other."""
        topic = research.get("topic", "").lower()
        design_topics = [
            d.get("spec", {}).get("informed_by", "").lower()
            for d in designs
        ]

        inconsistent = [
            d_name
            for d_name, d_topic in zip(
                [d.get("name", "?") for d in designs], design_topics
            )
            if d_topic and topic and d_topic != topic
        ]

        if inconsistent:
            self.issues.append(
                f"Inconsistent designs: {inconsistent}"
            )

        return {
            "passed": len(inconsistent) == 0,
            "topic_alignment": topic,
            "inconsistent_designs": inconsistent,
        }