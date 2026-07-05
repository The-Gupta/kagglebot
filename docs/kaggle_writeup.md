# 🤖 KaggleBot — AI-Powered Kaggle Competition Strategy Agent

## Track: Agents for Business

---

## The Problem

When a data scientist joins a Kaggle competition, the first **4–8 hours** are spent on repetitive discovery work before any real modeling begins:

1. **Reading** the competition overview, evaluation metric, and rules
2. **Profiling** the dataset — schema, types, nulls, distributions, target analysis
3. **Scouring** Discussion tabs for winning strategies and common pitfalls
4. **Synthesizing** all of this into a ranked ML strategy
5. **Writing** boilerplate baseline code

This is high-value work, but it's **predictable and pattern-driven** — exactly the kind of work an AI agent should automate.

## The Solution

> *"Analyze the Titanic competition and give me a ranked strategy with a baseline notebook."*

One sentence. KaggleBot reads the competition, profiles the data, researches winning approaches, and delivers a complete strategy document with working starter code — **all in minutes, not hours**.

Built with **Google Agent Development Kit (ADK)**, KaggleBot is a multi-agent system that orchestrates specialized agents to research, analyze, strategize, and generate code for any Kaggle competition.

---

## Architecture

```
User → Orchestrator → Scraper Agent → Data Agent → Strategy Agent → [HITL] → Code Agent
              ↕ memory tools
```

| Agent | Role | Tools |
|-------|------|-------|
| **Orchestrator** | Coordinator + memory | recall_learnings, store_learning, get_memory_stats |
| **Scraper Agent** | Competition researcher | scrape_competition_page, search_discussions |
| **Data Agent** | Dataset analyst | load_dataset, compute_profile, analyze_target, detect_issues |
| **Strategy Agent** | ML strategist | generate_strategies, save_strategy_report, approve_strategy |
| **Code Agent** | Baseline generator | generate_baseline_code, save_code_to_file |

---

## Concepts Demonstrated (11 total — 6 core + 5 bonus)

### Core Concepts

| # | Concept | Where | How |
|---|---------|-------|-----|
| 1 | **ADK (Multi-Agent)** | `agents/*.py` | 5-agent pipeline with sequential delegation |
| 2 | **MCP Servers** | `mcp_servers/*.py` | 3 servers with 8 tools for scraping, data, file I/O |
| 3 | **Antigravity** | Video | Entire project built using Antigravity IDE |
| 4 | **Security** | `security/*.py` | Input validation, secret scanning, AST code safety |
| 5 | **Deployability** | `deployment/` | Dockerfile + Cloud Run config + one-click deploy script |
| 6 | **Agent Skills** | `skills/*.py` | 4 modular skills (profiler, ranker, templates, memory) |

### Bonus Differentiators

| # | Concept | Where | How |
|---|---------|-------|-----|
| 7 | **Observability** | `observability/*.py` | OpenTelemetry-inspired tracing with tree visualization |
| 8 | **Evaluation** | `evaluation/*.py` | LLM-as-Judge with 5-criterion weighted rubric |
| 9 | **Memory** | `context/memory_manager.py` | Cross-session persistent learning with relevance scoring |
| 10 | **Sessions** | `context/session_manager.py` | Agent-to-agent data flow via session state keys |
| 11 | **HITL** | Strategy Agent | Mandatory user approval before code generation |

---

## Demo Walkthrough

```
User: "Analyze the Titanic competition"

🔍 Scraper Agent:
   ├── Title: Titanic - Machine Learning from Disaster
   ├── Type: Binary Classification | Metric: Accuracy
   └── Discussion insights: Feature engineering is king

📊 Data Agent:
   ├── 12 columns, 100 rows (sample)
   ├── Target: Survived (62% / 38%)
   ├── Missing: Age, Cabin (high nulls)
   └── Quality score: 89/100

📋 Strategy Agent (Ranked):
   #1: Logistic Regression Baseline (Low effort, Low risk)
   #2: Random Forest + Feature Engineering (Medium effort)
   #3: Gradient Boosting (Higher effort, Medium risk)

   ⏸️ [HITL] User approves Strategy #1

💻 Code Agent:
   → 141 lines of runnable Python baseline
   → Security checked: safe=True, no_secrets=True
```

---

## Project Stats

| Metric | Value |
|--------|-------|
| Total files | 43 (32 Python) |
| Lines of code | 5,239 |
| Agents | 5 |
| MCP tools | 8 |
| Skills | 4 |
| Security checks | 3 |
| E2E tests | 7/7 passing |
| Concepts | 11 (6 core + 5 bonus) |

---

## Links

- **GitHub**: [github.com/The-Gupta/kagglebot](https://github.com/The-Gupta/kagglebot)
- **YouTube Demo**: [VIDEO_URL]
- **Kaggle Notebook**: [NOTEBOOK_URL]

---

## Journey

This project was built over 9 days using Antigravity IDE:

| Day | What was built |
|-----|---------------|
| 1 | Foundation: scaffolding, orchestrator, web scraper MCP, scraper agent |
| 2 | Data pipeline: data MCP server (4 tools), data agent, profiler skill |
| 3 | Strategy + HITL: strategy ranker skill, strategy agent, file MCP server |
| 4 | Code gen + Security: code templates, code agent, 3 security modules |
| 5 | Memory: persistent cross-session learning with relevance scoring |
| 6 | Observability + Evaluation: tracing, trace viewer, LLM-as-Judge |
| 7 | Deployment + E2E Testing: Dockerfile, Cloud Run, 7/7 tests passing |
| 8 | Documentation: README, deployment guide, code cleanup |
| 9 | Notebook + Submission |

Every day produced working, tested code. The multi-agent architecture mirrors how an experienced Kaggler actually works: read the problem → look at the data → form a strategy → write code.

---

*Built with ❤️ using Google ADK + Antigravity IDE*
