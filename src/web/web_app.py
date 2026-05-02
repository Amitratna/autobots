#!/usr/bin/env python3
"""AI Agent Academy — Web Dashboard & API Server.

Serves a dark-themed web dashboard for the AI Agent Academy.
Includes a REST API and serves the frontend.

Usage:
    python web_app.py    # Starts on http://localhost:8080
"""

import json
import os
import random
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.data.lessons import LESSONS, LESSON_MAP, TOTAL_LESSONS

# ─── Progress ─────────────────────────────────────────────────────────

PROGRESS_DIR = Path.home() / ".aiacademy"
PROGRESS_FILE = PROGRESS_DIR / "progress.json"


def _load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def _save_progress(data: dict):
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(data, indent=2))


# ─── Frontend (loaded from dashboard.html) ──────────────────────────

HTML = Path(__file__).parent.joinpath("dashboard.html").read_text(encoding="utf-8")


# ─── HTTP Handler ─────────────────────────────────────────────────────

class AcademyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._send_html()

        elif path == "/api/lessons":
            self._send_json(LESSONS)

        elif path == "/api/progress":
            self._send_json(_load_progress())

        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if path == "/api/progress":
            lid = body.get("lessonId")
            score = body.get("score", 0)
            total = body.get("total", 0)
            completed = body.get("completed", False)
            p = _load_progress()
            sid = str(lid)
            if sid not in p:
                p[sid] = {}
            p[sid]["quiz_score"] = score
            p[sid]["quiz_total"] = total
            if completed:
                p[sid]["completed"] = True
            _save_progress(p)
            self._send_json({"status": "saved", "progress": p})

        elif path == "/api/agent/simulate":
            prompt = body.get("prompt", "")
            result = self._simulate_agent(prompt)
            self._send_json(result)

        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def _send_html(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, format, *args):
        sys.stderr.write(f"[Academy] {args[0]} {args[1]} {args[2]}\n")

    @staticmethod
    def _simulate_agent(prompt: str) -> dict:
        """Simulate an AI agent's thought process."""
        prompt_lower = prompt.lower()
        steps = []

        # Perception phase
        steps.append({
            "type": "perception",
            "content": f"Received input: \"{prompt[:80]}{'...' if len(prompt) > 80 else ''}\""
        })

        # Analyze what the user wants
        topics = []
        if any(w in prompt_lower for w in ["weather", "temperature", "forecast"]):
            topics.append("weather")
        if any(w in prompt_lower for w in ["news", "latest", "trending", "current"]):
            topics.append("news")
        if any(w in prompt_lower for w in ["ai", "agent", "llm", "machine learning", "learn"]):
            topics.append("ai_education")
        if any(w in prompt_lower for w in ["search", "find", "look up", "research"]):
            topics.append("research")
        if any(w in prompt_lower for w in ["write", "create", "generate", "make", "build"]):
            topics.append("content_creation")
        if any(w in prompt_lower for w in ["code", "program", "script", "function", "app"]):
            topics.append("coding")
        if not topics:
            topics.append("general")

        # Reasoning — identify intent
        reasoning_lines = [f"Analyzing query intent... detected topic: {topics[0]}"]
        if len(topics) > 1:
            reasoning_lines.append(f"Multiple intents detected: {', '.join(topics)}")

        if topics[0] == "ai_education":
            reasoning_lines.append("User is asking about AI/agent education")
            reasoning_lines.append("Retrieving relevant curriculum from knowledge base")
        elif topics[0] == "weather":
            reasoning_lines.append("User wants weather information")
            reasoning_lines.append("Need to call weather API tool")
        elif topics[0] == "research":
            reasoning_lines.append("User wants information retrieval")
            reasoning_lines.append("Need to call web_search tool")
        elif topics[0] == "coding":
            reasoning_lines.append("User wants code generation")
            reasoning_lines.append("Need to call code_interpreter tool")
        else:
            reasoning_lines.append("Processing general knowledge query")
            reasoning_lines.append("Searching knowledge base for relevant information")

        steps.append({
            "type": "reasoning",
            "content": "\n".join(reasoning_lines)
        })

        # Action — decide on tool
        if topics[0] == "ai_education":
            tool = "retrieve_knowledge"
            action_content = f"Calling retrieve_knowledge(topic='{prompt[:50]}')"
        elif topics[0] == "weather":
            tool = "get_weather"
            action_content = "Calling get_weather(location='auto')"
        elif topics[0] == "research":
            tool = "web_search"
            action_content = f"Calling web_search(query='{prompt[:50]}')"
        elif topics[0] == "coding":
            tool = "code_interpreter"
            action_content = "Calling code_interpreter(language='python')"
        else:
            tool = "knowledge_base"
            action_content = "Calling knowledge_base.query()"

        steps.append({
            "type": "action",
            "tool": tool,
            "content": action_content
        })

        # Result
        if topics[0] == "ai_education":
            result = (
                "🤖 **AI Academy Insights**\n\n"
                "Here's what I know:\n"
                "1. AI Agents are autonomous programs that perceive, reason, and act\n"
                "2. The core architecture follows Perception → Reasoning → Action loop\n"
                "3. Agents use tools (function calling) to interact with the outside world\n"
                "4. Memory (short-term + long-term) lets agents remember context\n"
                "5. Multi-agent systems use specialized agents working together\n\n"
                "Want to dive deeper? Check out Lesson 1: What is an AI Agent? or visit our "
                "Agent Playground to experiment!"
            )
        elif topics[0] == "weather":
            result = "I would check a weather API. In this simulated environment: ☀️ 22°C, mostly sunny. (Connect a real weather API for live data.)"
        elif topics[0] == "coding":
            result = (
                "I can help you write code! Here's a simple agent function:\n\n"
                "def simple_agent(prompt, tools):\n"
                "    response = llm.chat(prompt)\n"
                "    if 'search' in prompt:\n"
                "        return tools['web_search'](prompt)\n"
                "    return response\n\n"
                "Try Lesson 6: Building Your First Agent for a full walkthrough."
            )
        else:
            result = (
                f"Great question! Based on my knowledge base, here's what I found about \"{prompt[:60]}...\":\n\n"
                "This is a simulated agent response. In a production agent, this is where "
                "I'd provide the actual information retrieved from tools, APIs, or databases.\n\n"
                "💡 Tip: Try asking about AI agents, coding with agents, or weather to see different agent behaviors!"
            )

        steps.append({
            "type": "result",
            "content": result
        })

        return {
            "steps": steps,
            "answer": result,
            "tools_used": [tool],
            "tokens_used": random.randint(80, 300),
        }


# ─── Entry point ──────────────────────────────────────────────────────

def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), AcademyHandler)
    print(f"🤖 AI Agent Academy running at:")
    print(f"   📚 Web Dashboard: http://localhost:{port}")
    print(f"   📡 API Server:    http://localhost:{port}/api/")
    print(f"\nProgress saved to: {PROGRESS_FILE}")
    print(f"\nPress Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()