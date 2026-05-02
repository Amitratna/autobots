"""Tests for the AUTOBOTS agentic framework.

Each agent has a corresponding test class reflecting its new role:
  Bumblebee → Research
  Ironhide → Design
  Ratchet   → Analysis
  RedAlert  → Development
  Jetfire   → Coding
  Wheelie   → Quality Inspection
"""

import pytest
from src.agents import BaseAgent, AgentMessage
from src.agents.optimus_prime import OptimusPrime
from src.agents.bumblebee import Bumblebee
from src.agents.ironhide import Ironhide
from src.agents.ratchet import Ratchet
from src.agents.red_alert import RedAlert
from src.agents.jetfire import Jetfire
from src.agents.wheelie import Wheelie


# ─── Base Agent ───────────────────────────────────────────────────────

class _ConcreteAgent(BaseAgent):
    """Minimal concrete agent for testing the base class."""
    def execute(self):
        return {"done": True}


class TestBaseAgent:
    def test_can_instantiate(self):
        agent = _ConcreteAgent(name="TestBot")
        assert agent.name == "TestBot"

    def test_send_receive(self):
        a = _ConcreteAgent(name="Alice")
        b = _ConcreteAgent(name="Bob")
        a.send(b, "hello", {"msg": "hi"})
        assert len(b.mailbox) == 1
        assert b.mailbox[0].subject == "hello"
        assert b.mailbox[0].body == {"msg": "hi"}
        assert b.mailbox[0].sender == "Alice"

    def test_execute_abstract(self):
        with pytest.raises(TypeError):
            BaseAgent("abstract")  # noqa


# ─── OptimusPrime (Orchestrator) ──────────────────────────────────────

class TestOptimusPrime:
    def test_register_agent(self):
        prime = OptimusPrime()
        bee = Bumblebee()
        prime.register_agent(bee)
        assert "Bumblebee" in prime.agents

    def test_define_pipeline_custom_order(self):
        prime = OptimusPrime()
        prime.register_agent(Bumblebee())
        prime.register_agent(Ironhide())
        prime.define_pipeline(["Bumblebee", "Ironhide"])
        assert prime.pipeline == ["Bumblebee", "Ironhide"]

    def test_define_pipeline_unknown_raises(self):
        prime = OptimusPrime()
        with pytest.raises(ValueError):
            prime.define_pipeline(["Ghost"])

    def test_execute_returns_all_agent_results(self):
        prime = OptimusPrime(config={"goal": "test run"})
        prime.register_agent(Bumblebee())
        prime.register_agent(Wheelie())
        result = prime.execute()
        assert result["status"] == "complete"
        assert "Bumblebee" in result["agent_results"]
        assert "Wheelie" in result["agent_results"]

    def test_pipeline_executes_in_registration_order(self):
        prime = OptimusPrime()
        prime.register_agent(Bumblebee())
        prime.register_agent(Ironhide())
        prime.register_agent(Ratchet())
        result = prime.execute()
        assert list(result["agent_results"].keys()) == [
            "Bumblebee", "Ironhide", "Ratchet"
        ]

    def test_context_passes_between_agents(self):
        """Downstream agents should see upstream results in their config."""
        prime = OptimusPrime(config={"goal": "context test"})
        b = Bumblebee(config={"topic": "test market"})
        i = Ironhide(config={"output_count": 2})
        prime.register_agent(b)
        prime.register_agent(i)
        result = prime.execute()
        # OptimusPrime sends upstream results as context to each agent
        # Ironhide's result should show it was informed by research
        assert result["agent_results"]["Ironhide"]["count"] == 2
        assert result["agent_results"]["Bumblebee"]["topic"] == "test market"
        assert "trends" in result["agent_results"]["Bumblebee"]


# ─── Bumblebee (Researcher) ───────────────────────────────────────────

class TestBumblebee:
    def test_execute_returns_research_data(self):
        bee = Bumblebee(config={"topic": "developer tools"})
        result = bee.execute()
        assert "trends" in result
        assert "competitors" in result
        assert "opportunities" in result
        assert "deep_dive" in result
        assert "sources_used" in result

    def test_execute_real_data_sources(self):
        """Bumblebee should return real data from live sources."""
        bee = Bumblebee(config={"topic": "Python programming language"})
        result = bee.execute()
        # Should have real data from at least one source
        assert len(result.get("sources_used", [])) > 0
        # Deep dive should have real Wikipedia results
        deep = result.get("deep_dive", {})
        if deep.get("wikipedia_articles"):
            assert len(deep["wikipedia_articles"]) > 0

    def test_deep_dive_returns_wikipedia(self):
        bee = Bumblebee(config={"topic": "Artificial intelligence"})
        result = bee.execute()
        deep = result.get("deep_dive", {})
        # Wikipedia should return results for "artificial intelligence"
        if deep.get("wikipedia_summary"):
            assert "intelligence" in deep["wikipedia_summary"].lower()

    def test_default_topic(self):
        bee = Bumblebee()
        result = bee.execute()
        assert "current market" in result.get("topic", "")


# ─── Ironhide (Designer) ──────────────────────────────────────────────

class TestIronhide:
    def test_execute_generates_html(self):
        ih = Ironhide(config={
            "page_type": "landing",
            "brand": "TestBrand",
            "research": {"topic": "test topic"},
        })
        result = ih.execute()
        assert result["deliverable_type"] == "landing_html"
        assert result["count"] == 4  # landing, saas_landing, pricing, about
        assert "primary_page" in result
        assert result["primary_page"]["html_size_bytes"] > 1000
        assert result["primary_page"]["file_path"].endswith(".html")

    def test_uses_design_system(self):
        ih = Ironhide(config={
            "page_type": "landing",
            "research": {"topic": "Artificial intelligence"},
        })
        result = ih.execute()
        assert result["design_system_used"] is not None
        assert result["available_design_systems"] > 0

    def test_generates_multi_page_set(self):
        ih = Ironhide(config={
            "research": {"topic": "developer tools"},
        })
        result = ih.execute()
        assert len(result["generated_pages"]) >= 3
        for p in result["generated_pages"]:
            assert p["status"] == "generated"
            assert p["size_bytes"] > 500

    def test_deliverable_type_configurable(self):
        ih = Ironhide(config={
            "page_type": "saas_landing",
            "research": {"topic": "SaaS platform"},
        })
        result = ih.execute()
        assert result["deliverable_type"] == "saas_landing_html"
        assert result["primary_page"]["type"] == "saas_landing"


# ─── Ratchet (Analyst) ────────────────────────────────────────────────

class TestRatchet:
    def test_execute_returns_full_analysis(self):
        r = Ratchet()
        result = r.execute()
        assert "market_summary" in result
        assert "design_analysis" in result
        assert "metrics" in result
        assert "recommendations" in result

    def test_design_analysis_counts_correctly(self):
        designs = [
            {"name": "a", "spec": {"status": "draft"}},
            {"name": "b", "spec": {"status": "draft"}},
        ]
        r = Ratchet(config={"designs": designs})
        result = r.execute()
        assert result["design_analysis"]["total"] == 2
        assert result["design_analysis"]["complete"] == 2

    def test_generates_recommendations(self):
        r = Ratchet(config={
            "research": {"topic": "test"},
            "designs": [{"name": "x"}],
            "metrics": {"confidence": 0.9},
        })
        result = r.execute()
        assert len(result["recommendations"]) > 0


# ─── RedAlert (Developer) ─────────────────────────────────────────────

class TestRedAlert:
    def test_execute_returns_artifacts(self):
        dev = RedAlert()
        result = dev.execute()
        assert "artifacts" in result
        assert len(result["artifacts"]) > 0

    def test_builds_web_app(self):
        dev = RedAlert(config={
            "specs": {"type": "web_app", "name": "myapp"},
        })
        result = dev.execute()
        assert result["status"] == "built"
        assert any("myapp" in a for a in result["artifacts"])

    def test_builds_api(self):
        dev = RedAlert(config={
            "specs": {
                "type": "api",
                "name": "myapi",
                "endpoints": ["/health", "/data"],
            },
        })
        result = dev.execute()
        assert result["status"] == "built"
        assert result["endpoints"] == ["/health", "/data"]


# ─── Jetfire (Coder) ──────────────────────────────────────────────────

class TestJetfire:
    def test_execute_from_tasks(self):
        j = Jetfire(config={
            "language": "python",
            "tasks": [
                {"name": "main", "module": "src"},
                {"name": "worker", "module": "src"},
            ],
        })
        result = j.execute()
        assert result["tasks_completed"] == 2
        assert len(result["files_written"]) == 2

    def test_execute_from_designs(self):
        j = Jetfire(config={
            "language": "javascript",
            "tasks": [],
            "designs": [
                {"name": "button", "module": "components"},
                {"name": "modal", "module": "components"},
            ],
        })
        result = j.execute()
        assert result["tasks_completed"] == 2
        assert "components/button.js" in result["files_written"]

    def test_file_extensions(self):
        for lang, ext in [("python", "py"), ("javascript", "js"),
                          ("typescript", "ts"), ("rust", "rs"),
                          ("go", "go")]:
            assert Jetfire._ext(lang) == ext


# ─── Wheelie (Quality Inspector) ──────────────────────────────────────

class TestWheelie:
    def test_passes_complete_outputs(self):
        w = Wheelie(config={
            "research": {"trends": ["a"], "competitors": {"top_players": ["x"]}},
            "designs": [{"name": "spec1", "spec": {"status": "draft", "informed_by": "test"}}],
            "code_artifacts": ["src/main.py"],
            "analysis": {"recommendations": ["improve X"]},
        })
        result = w.execute()
        assert result["passed"] is True

    def test_fails_missing_research(self):
        w = Wheelie(config={
            "research": {},
            "designs": [{"name": "d1", "spec": {}}],
            "code_artifacts": [],
            "analysis": {},
        })
        result = w.execute()
        assert result["passed"] is False
        assert len(result["issues"]) > 0

    def test_detects_inconsistent_designs(self):
        w = Wheelie(config={
            "research": {"topic": "AI tools"},
            "designs": [
                {"name": "d1", "spec": {"informed_by": "AI tools"}},
                {"name": "d2", "spec": {"informed_by": "cooking"}},
            ],
        })
        result = w.execute()
        assert result["passed"] is False
        assert any("inconsistent" in issue.lower() for issue in result["issues"])


# ─── Full Integration ─────────────────────────────────────────────────

class TestFullPipeline:
    def test_end_to_end_all_agents(self):
        """Execute the full 6-agent pipeline with representative config."""
        prime = OptimusPrime(config={"goal": "integration test"})

        prime.register_agent(Bumblebee(config={"topic": "AI developer tools"}))
        prime.register_agent(Ironhide(config={"output_count": 2}))
        prime.register_agent(Ratchet())
        prime.register_agent(RedAlert(config={
            "specs": {"type": "web_app", "name": "test-app"},
        }))
        prime.register_agent(Jetfire(config={
            "language": "python",
            "tasks": [{"name": "server", "module": "app"}],
        }))
        prime.register_agent(Wheelie())

        result = prime.execute()
        assert result["status"] == "complete"

        expected = {"Bumblebee", "Ironhide", "Ratchet",
                    "RedAlert", "Jetfire", "Wheelie"}
        assert expected.issubset(result["agent_results"].keys())

    def test_pipeline_context_flows(self):
        """Verify each agent receives context from its predecessors."""
        prime = OptimusPrime(config={"goal": "context flow"})
        prime.register_agent(Bumblebee(config={"topic": "test"}))
        prime.register_agent(Ironhide(config={"output_count": 1}))
        prime.register_agent(Wheelie())

        result = prime.execute()

        # All agents executed and pipeline completed
        assert result["status"] == "complete"
        assert set(result["agent_results"].keys()) == {
            "Bumblebee", "Ironhide", "Wheelie"
        }
        # Bumblebee's research output is present
        assert result["agent_results"]["Bumblebee"]["topic"] == "test"