# AUTOBOTS Agentic Framework

A 7-agent autonomous workforce for creating and selling digital illustration brushes on Etsy and Gumroad.

## Architecture

```
OptimusPrime (Orchestrator)
├── Bumblebee (Researcher) — market trends, competitor analysis
├── Ironhide (Designer) — generates brush designs via AI
├── Ratchet (Tester) — validates quality & consistency
├── RedAlert (Developer) — builds dashboards & tooling
├── Jetfire (Deployment) — packages & ships to platforms
└── Wheelie (Marketer) — creates campaigns & listing copy
```

## Tech Stack

- Python 3.11+
- Hermes Agent (delegate_task for agent orchestration)
- NVIDIA AI APIs (image generation)
- Etsy & Gumroad APIs (listing & sales)

## Setup

```bash
cd autobots
chmod +x setup.sh
./setup.sh
```

## Usage

```bash
python -m src.main
```