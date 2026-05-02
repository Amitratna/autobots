"""Tests for the AUTOBOTS agentic framework.

Each agent has a corresponding test class. Tests are written TDD-style:
write the failing test first, then implement until it passes.
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


# ─── OptimusPrime ─────────────────────────────────────────────────────

class TestOptimusPrime:
    def test_register_agent(self):
        prime = OptimusPrime()
        bee = Bumblebee()
        prime.register_agent(bee)
        assert "Bumblebee" in prime.agents

    def test_define_pipeline(self):
        prime = OptimusPrime()
        prime.register_agent(Bumblebee())
        prime.register_agent(Ironhide())
        prime.define_pipeline(["Bumblebee", "Ironhide"])
        assert prime.pipeline == ["Bumblebee", "Ironhide"]

    def test_define_pipeline_unknown_agent(self):
        prime = OptimusPrime()
        with pytest.raises(ValueError):
            prime.define_pipeline(["Ghost"])

    def test_execute_returns_results(self):
        prime = OptimusPrime(config={"goal": "test"})
        prime.register_agent(Bumblebee())
        result = prime.execute()
        assert result["status"] == "complete"
        assert "Bumblebee" in result["agent_results"]

    def test_pipeline_executes_in_order(self):
        prime = OptimusPrime()
        for ag in [Bumblebee(), Ironhide(), Wheelie()]:
            prime.register_agent(ag)
        result = prime.execute()
        assert list(result["agent_results"].keys()) == [
            "Bumblebee", "Ironhide", "Wheelie"
        ]


# ─── Bumblebee ────────────────────────────────────────────────────────

class TestBumblebee:
    def test_execute_returns_research(self):
        bee = Bumblebee(config={"niche": "test brushes"})
        result = bee.execute()
        assert "trending_styles" in result
        assert "price_points" in result
        assert "keywords" in result
        assert "competitors" in result

    def test_default_niche(self):
        bee = Bumblebee()
        result = bee.execute()
        assert "digital illustration brushes" in result["niche"]


# ─── Ironhide ─────────────────────────────────────────────────────────

class TestIronhide:
    def test_execute_returns_designs(self):
        ironhide = Ironhide(config={
            "brush_count": 3,
            "research": {"trending_styles": ["watercolour"]},
        })
        result = ironhide.execute()
        assert result["count"] == 3
        assert len(result["designs"]) == 3

    def test_each_design_has_required_fields(self):
        ironhide = Ironhide(config={"brush_count": 1})
        result = ironhide.execute()
        d = result["designs"][0]
        assert "name" in d
        assert "description" in d
        assert "type" in d
        assert "parameters" in d


# ─── Ratchet ─────────────────────────────────────────────────────────

class TestRatchet:
    @pytest.fixture
    def good_designs(self):
        return [
            {"name": "a1", "description": "desc", "parameters": {"size": "x", "opacity": "y", "texture": "z"}},
            {"name": "a2", "description": "desc", "parameters": {"size": "x", "opacity": "y", "texture": "z"}},
        ]

    @pytest.fixture
    def bad_designs(self):
        return [
            {"name": "", "description": "", "parameters": {}},
            {"name": "b1", "description": "ok", "parameters": {"size": "x"}},
        ]

    def test_passes_good_designs(self, good_designs):
        r = Ratchet(config={"designs": good_designs})
        result = r.execute()
        assert result["passed"] is True

    def test_fails_bad_designs(self, bad_designs):
        r = Ratchet(config={"designs": bad_designs})
        result = r.execute()
        assert result["passed"] is False
        assert len(result["issues"]) > 0

    def test_detects_duplicate_names(self):
        designs = [
            {"name": "dup", "description": "d1", "parameters": {"size": "x", "opacity": "y", "texture": "z"}},
            {"name": "dup", "description": "d2", "parameters": {"size": "x", "opacity": "y", "texture": "z"}},
        ]
        r = Ratchet(config={"designs": designs})
        result = r.execute()
        assert result["passed"] is False
        assert any("Duplicate" in issue for issue in result["issues"])


# ─── RedAlert ────────────────────────────────────────────────────────

class TestRedAlert:
    def test_execute_returns_artifacts(self):
        dev = RedAlert()
        result = dev.execute()
        assert "artifacts" in result
        assert len(result["artifacts"]) > 0

    def test_dashboard_component(self):
        dev = RedAlert(config={"component": "dashboard"})
        result = dev.execute()
        assert any("dashboard" in a for a in result["artifacts"])


# ─── Jetfire ─────────────────────────────────────────────────────────

class TestJetfire:
    def test_execute_returns_deployments(self):
        designs = [{"name": f"brush_{i}"} for i in range(15)]
        j = Jetfire(config={"designs": designs, "platforms": ["etsy"]})
        result = j.execute()
        assert len(result["deployments"]) == 1
        assert result["deployments"][0]["platform"] == "etsy"

    def test_bundles_into_packs(self):
        designs = [{"name": f"brush_{i}"} for i in range(25)]
        j = Jetfire(config={"designs": designs, "pack_size": 10})
        result = j.execute()
        # 25 designs / 10 per pack = 3 packs
        assert result["deployments"][0]["packs_created"] == 3


# ─── Wheelie ─────────────────────────────────────────────────────────

class TestWheelie:
    def test_execute_returns_campaigns(self):
        packs = [
            {"name": "Watercolour Pack", "count": 10},
            {"name": "Marker Pack", "count": 8},
        ]
        w = Wheelie(config={"packs": packs, "research": {"keywords": ["art", "brushes"]}})
        result = w.execute()
        assert len(result["campaigns"]) == 2

    def test_generates_title_with_count(self):
        w = Wheelie()
        title = w._generate_title("Test Pack", 10)
        assert "10" in title
        assert "Test Pack" in title


# ─── Integration ─────────────────────────────────────────────────────

class TestFullPipeline:
    def test_end_to_end(self):
        """Run the full pipeline and verify all agents produce output."""
        prime = OptimusPrime(config={"goal": "test run"})
        prime.register_agent(Bumblebee())
        prime.register_agent(Ironhide(config={"brush_count": 3}))
        prime.register_agent(Ratchet())
        prime.register_agent(RedAlert())
        prime.register_agent(Jetfire(config={"pack_size": 5}))
        prime.register_agent(Wheelie())

        result = prime.execute()
        assert result["status"] == "complete"

        expected_agents = {
            "Bumblebee", "Ironhide", "Ratchet",
            "RedAlert", "Jetfire", "Wheelie",
        }
        assert expected_agents.issubset(result["agent_results"].keys())