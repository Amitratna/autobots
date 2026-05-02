"""Jetfire — Coder Agent.

Writes production-ready code: scripts, modules, features, refactors.
Implements what RedAlert designs — the engineering workhorse.
"""

from typing import Any, Dict, List
from src.agents import BaseAgent


class Jetfire(BaseAgent):
    """Coder — writes, reviews, and refactors production code."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(name="Jetfire", config=config)
        self.files_written: List[str] = []

    def execute(self) -> Dict[str, Any]:
        """Implement code based on design specs and tasks."""
        tasks = self.config.get("tasks", [])
        language = self.config.get("language", "python")
        designs = self.config.get("designs", [])

        results = []
        for task in tasks:
            result = self._implement_task(task, language)
            results.append(result)

        # If no explicit tasks, derive from designs
        if not tasks and designs:
            for design in designs:
                result = self._implement_from_design(design, language)
                results.append(result)

        return {
            "language": language,
            "files_written": self.files_written,
            "tasks_completed": len(results),
            "results": results,
        }

    def _implement_task(self, task: dict, language: str) -> dict:
        """Implement a single coding task."""
        task_name = task.get("name", "unnamed")
        module = task.get("module", "src")
        self.files_written.append(f"{module}/{task_name}.{self._ext(language)}")
        return {
            "task": task_name,
            "status": "stub",
            "file": f"{module}/{task_name}.{self._ext(language)}",
        }

    def _implement_from_design(self, design: dict, language: str) -> dict:
        """Implement code derived from a design spec."""
        name = design.get("name", "component")
        module = design.get("module", "src")
        ext = self._ext(language)
        path = f"{module}/{name}.{ext}"
        self.files_written.append(path)
        return {
            "design": name,
            "status": "stub",
            "file": path,
        }

    @staticmethod
    def _ext(language: str) -> str:
        return {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "rust": "rs",
            "go": "go",
            "java": "java",
            "html": "html",
            "css": "css",
        }.get(language, "txt")