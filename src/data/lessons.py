"""Lesson content for AI Agent Academy."""

LESSONS = [
    {
        "id": 1,
        "title": "What is an AI Agent?",
        "summary": "Understand the core concept of an AI agent — an autonomous program that perceives, reasons, and acts.",
        "content": """
# What is an AI Agent?

An **AI agent** is a software program that can:
- **Perceive** its environment (via input, APIs, sensors)
- **Reason** about what to do (using an LLM or rule engine)
- **Act** autonomously to achieve a goal

## Key Characteristics

- **Autonomy** — operates without human intervention
- **Goal-oriented** — works toward a defined objective
- **Reactive** — responds to changes in environment
- **Proactive** — can take initiative

## Examples

| Type | Example |
|------|---------|
| Chatbot | Customer support assistant |
| Coding Agent | GitHub Copilot, Cursor |
| Research Agent | AutoGPT, AgentGPT |
| Automation | Zapier bots, email filters |

## Analogy

Think of an AI agent like a smart intern:
- You give them a goal ("research competitors")
- They figure out the steps
- They report back when done
- You only step in if something goes wrong
""",
        "quiz_questions": [
            {
                "question": "What is a defining characteristic of an AI agent?",
                "options": ["Needs constant human input", "Operates autonomously toward a goal", "Must run on GPU", "Can only process text"],
                "correct": 1
            },
            {
                "question": "Which of these is an example of an AI agent?",
                "options": ["A calculator app", "GitHub Copilot", "A text editor", "An operating system"],
                "correct": 1
            },
            {
                "question": "An AI agent that takes initiative without being told is called:",
                "options": ["Reactive", "Proactive", "Passive", "Static"],
                "correct": 1
            }
        ]
    },
    {
        "id": 2,
        "title": "Agent Architecture",
        "summary": "Learn the fundamental architecture: Perception → Reasoning → Action loop.",
        "content": """
# Agent Architecture

Every AI agent follows a core loop:

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│PERCEPTION│───▶│ REASONING│───▶│  ACTION  │
│  (Input) │    │  (Think) │    │  (Do)    │
└──────────┘    └──────────┘    └──────────┘
      ▲                               │
      └─────────── LOOP ──────────────┘
```

## 1. Perception
The agent receives input from its environment:
- User messages
- File contents
- API responses
- Sensor data
- System state

## 2. Reasoning
The agent processes the input using:
- An LLM (GPT, Claude, Llama)
- Rules and logic
- Past memory and context
- Available tools

## 3. Action
The agent executes a decision:
- Responds with text
- Calls a function/tool
- Modifies files
- Makes API calls
- Takes physical action (robotics)

## The Loop Never Stops

Agents continuously cycle through perception → reasoning → action until the goal is achieved or a stopping condition is met.
""",
        "quiz_questions": [
            {
                "question": "What is the correct order of the agent loop?",
                "options": ["Action → Reasoning → Perception", "Perception → Reasoning → Action", "Reasoning → Action → Perception", "Perception → Action → Reasoning"],
                "correct": 1
            },
            {
                "question": "What happens after an agent takes an action?",
                "options": ["The agent shuts down", "The loop continues with new perception", "The agent waits for human approval", "Nothing"],
                "correct": 1
            },
            {
                "question": "Which component of the agent loop uses an LLM?",
                "options": ["Perception", "Reasoning", "Action", "All three"],
                "correct": 1
            }
        ]
    },
    {
        "id": 3,
        "title": "Tools & Function Calling",
        "summary": "How agents use tools — APIs, functions, and external capabilities — to extend their reach.",
        "content": """
# Tools & Function Calling

Agents are powerful, but they're limited without **tools**. A tool is any function an agent can call to interact with the outside world.

## Why Tools Matter

An LLM alone can only generate text. With tools, an agent can:
- Search the web
- Read/write files
- Run code
- Send emails
- Query databases
- Control devices

## How Function Calling Works

```
User: "What's the weather in Tokyo?"

Agent thinks: I need to check the weather
Agent calls: get_weather("Tokyo")
  → Returns "22°C, sunny"

Agent responds: "The weather in Tokyo is 22°C and sunny!"
```

## Common Tool Types

| Tool | Example | Use |
|------|---------|-----|
| Search | web_search(query) | Find information |
| Calculator | calculate(expr) | Math operations |
| File I/O | read_file(path) | Access documents |
| Code exec | run_python(code) | Execute scripts |
| HTTP | fetch(url) | API calls |

## Safety & Guardrails

Good agents have:
- Tool permissions (what can be called)
- Rate limits (prevent abuse)
- Confirmation gates (dangerous actions need approval)
- Sandboxing (run code in isolated environment)
""",
        "quiz_questions": [
            {
                "question": "Why do AI agents need tools?",
                "options": ["To look more impressive", "To interact with the real world beyond text", "To replace APIs", "They don't — tools are optional"],
                "correct": 1
            },
            {
                "question": "What is function calling in AI agents?",
                "options": ["Calling a phone number", "The agent executing a predefined function/tool", "Writing functions in Python", "Debugging code"],
                "correct": 1
            },
            {
                "question": "Which is NOT a common agent tool?",
                "options": ["Web search", "Code execution", "File reading", "Screen mirroring"],
                "correct": 3
            }
        ]
    },
    {
        "id": 4,
        "title": "Memory & Context",
        "summary": "How agents remember information across conversations and sessions using short-term and long-term memory.",
        "content": """
# Memory & Context

Memory is what separates a useful agent from a forgetful one.

## Types of Memory

### Short-term (working memory)
- The current conversation
- Recent tool outputs
- The immediate task context
- Reset each session

### Long-term (persistent memory)
- User preferences and facts
- Past conversations summaries
- Learned patterns
- Stored in vector databases or JSON files

### Episodic memory
- Records of past interactions
- What worked / what didn't
- Helps improve over time

## How Agents Use Memory

```
User: "Remember my name is Amit"

Agent stores: {user_id: "Amit"}

User: "What's my name?"
Agent retrieves: "Amit"
Agent responds: "Your name is Amit!"
```

## Context Window Limits

Every LLM has a maximum context window:
- Claude: 200K tokens
- GPT-4: 128K tokens
- Llama 3: 8K-128K tokens

When context gets too long, agents must:
1. **Summarize** — compress old messages
2. **Prune** — remove irrelevant content
3. **RAG** — retrieve relevant info on demand
""",
        "quiz_questions": [
            {
                "question": "What type of memory stores user preferences across sessions?",
                "options": ["Short-term memory", "Long-term memory", "Episodic memory", "Cache memory"],
                "correct": 1
            },
            {
                "question": "What happens when an agent's context is too long?",
                "options": ["The agent crashes", "The agent must summarize or prune", "The agent restarts", "Nothing — infinite context"],
                "correct": 1
            },
            {
                "question": "What does RAG stand for?",
                "options": ["Random Access Generation", "Retrieval-Augmented Generation", "Real-time Agent Gateway", "Reasoning and Guessing"],
                "correct": 1
            }
        ]
    },
    {
        "id": 5,
        "title": "Multi-Agent Systems",
        "summary": "How multiple agents work together — delegation, specialization, and orchestration patterns.",
        "content": """
# Multi-Agent Systems

Sometimes one agent isn't enough. Multi-agent systems use **multiple specialized agents** working together.

## Why Multiple Agents?

- **Specialization** — each agent has a focused role
- **Parallelism** — agents work simultaneously
- **Resilience** — one failing doesn't stop everything
- **Scalability** — add more agents as needed

## Common Architectures

### Sequential Pipeline
```
Agent A → Agent B → Agent C → Result
```
Each agent feeds into the next. Good for predictable workflows.

### Hub & Spoke (Orchestrator)
```
          ┌── Agent A ──┐
          │              │
Orchestrator ── Agent B ── Result
          │              │
          └── Agent C ──┘
```
A central orchestrator delegates tasks and synthesises results.

### Debate / Ensemble
```
Agent A ──┐
          ├── Arbiter → Final Answer
Agent B ──┘
```
Multiple agents produce answers, an arbiter picks the best.

## Example: AUTOBOTS

This very framework uses a 6-agent pipeline:
1. Bumblebee (Research)
2. Ironhide (Design)
3. Ratchet (Analysis)
4. RedAlert (Development)
5. Jetfire (Coding)
6. Wheelie (QA)
""",
        "quiz_questions": [
            {
                "question": "What is a key benefit of multi-agent systems?",
                "options": ["Slower execution", "Agent specialization", "More code to write", "Single point of failure"],
                "correct": 1
            },
            {
                "question": "In a hub-and-spoke architecture, what does the hub do?",
                "options": ["Nothing", "Delegates tasks and synthesises results", "Does all the work alone", "Monitors system health"],
                "correct": 1
            },
            {
                "question": "Which AUTOBOTS agent is the orchestrator?",
                "options": ["Bumblebee", "OptimusPrime", "Jetfire", "Wheelie"],
                "correct": 1
            }
        ]
    },
    {
        "id": 6,
        "title": "Building Your First Agent",
        "summary": "A practical walkthrough of building a simple AI agent using Python, an LLM API, and function calling.",
        "content": """
# Building Your First Agent

Let's build a simple research agent that can search the web and answer questions.

## Step 1: Define the tools

```python
def web_search(query: str) -> list:
    '''Search the web and return results.'''
    import requests
    response = requests.get(
        "https://api.duckduckgo.com",
        params={"q": query, "format": "json"}
    )
    return response.json().get("results", [])
```

## Step 2: The agent loop

```python
def agent_loop(user_input: str, tools: dict):
    messages = [{"role": "user", "content": user_input}]

    while True:
        # 1. Send to LLM
        response = llm.chat(messages)

        # 2. Check if LLM wants to use a tool
        tool_call = response.get("tool_calls")
        if not tool_call:
            return response["content"]  # Final answer

        # 3. Execute the tool
        func = tools[tool_call["name"]]
        result = func(**tool_call["arguments"])

        # 4. Feed result back to LLM
        messages.append(tool_call)
        messages.append({"role": "tool", "content": str(result)})
```

## Step 3: Put it together

```python
tools = {"web_search": web_search, "calculator": calculate}
result = agent_loop("What's the population of Japan?", tools)
print(result)
# Output: "The population of Japan is approximately 125 million."
```

## Key Takeaways

- Start simple — a single agent loop with 2-3 tools
- Add memory as you grow
- Test with real user queries
- Add guardrails before deploying

## Next Steps

- Try building this yourself in our Agent Playground tab
- Experiment with different tool combinations
- Add persistent memory
- Scale to multiple agents
""",
        "quiz_questions": [
            {
                "question": "What is the first step in the agent loop?",
                "options": ["Execute a tool", "Send the user input to an LLM", "Save to memory", "Return the final answer"],
                "correct": 1
            },
            {
                "question": "How does the agent decide to use a tool?",
                "options": ["It always uses all tools", "The LLM responds with a tool_call", "The user tells it to", "Random selection"],
                "correct": 1
            },
            {
                "question": "What happens to the tool result?",
                "options": ["It's discarded", "It's fed back into the LLM as context", "It's saved to a file", "It's ignored"],
                "correct": 1
            }
        ]
    }
]

LESSON_MAP = {lesson["id"]: lesson for lesson in LESSONS}
TOTAL_LESSONS = len(LESSONS)