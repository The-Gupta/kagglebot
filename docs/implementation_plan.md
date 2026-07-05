# Implementation Plan — KaggleBot

## Fact-Check Summary

Before building, I verified our problem statement against the actual competition page and course syllabus. Here are the corrections needed and the updated plan.

---

## Critical Corrections to Problem Statement

> [!CAUTION]
> ### Issues Found in Our Spec

| Item | Our Spec Said | Actual Requirement | Impact |
|---|---|---|---|
| **Official concept list** | Sessions & Memory, Observability, Agent Evaluation | **Agent/Multi-agent (ADK), MCP Servers, Antigravity, Security features, Deployability, Agent Skills** | 🔴 **Critical** — we must demonstrate ≥3 of the 6 *official* concepts |
| **Rubric: The Pitch** | 10 + 10 + 10 = 30 pts | **Core Concept & Value (15 pts) + Writeup (15 pts) = 30 pts**. Video is evaluated but points are within these categories | 🟡 Minor — total still 30 |
| **Rubric: Implementation** | Tech (50) + Docs (20) = 70 | **70 pts total** for implementation quality. README (20 pts) is part of this | 🟡 Minor — close enough |
| **Bonus points** | Not mentioned | **+20 bonus pts** (added to Cat 1 + Cat 2, capped at 100 total) | 🟡 New info — opportunity |
| **Submission: Public project link** | Not mentioned | **Required** — must include a publicly accessible URL to working product/demo | 🔴 **Important** — need a deployed/accessible version |
| **Team size** | Up to 4 | Up to **5** | 🟢 Minor |

---

## Updated Concept Strategy

### The 6 Official Concepts (must demonstrate ≥3)

| # | Official Concept | Demonstrate Via | Our Plan | Status |
|---|---|---|---|---|
| 1 | **Agent / Multi-agent systems (ADK)** | Code | 5 agents (Orchestrator + 4 sub-agents) | ✅ Already planned |
| 2 | **MCP Servers** | Code | 3 MCP servers (Web Scraper, Data, File) | ✅ Already planned |
| 3 | **Antigravity** | Video | Record clips of KaggleBot being developed in Antigravity IDE | ✅ Planned — recording IDE development process |
| 4 | **Security features** | Code or Video | Input validation, no API keys in code, safe code generation | ✅ Planned |
| 5 | **Deployability** | Video + Code | Dockerfile + Cloud Run config. Show deployment in video | ✅ **Planned** — Dockerfile + `cloudbuild.yaml` |
| 6 | **Agent Skills** | Code or Video | Modular skills (profiler, ranker, templates, memory) | ✅ Planned |

> [!TIP]
> **We will demonstrate ALL 6 of 6 official concepts.** This is the maximum possible coverage and puts us ahead of nearly every other submission.

### Bonus Concepts (not in the official 6 but still impressive)

These don't count toward the "3 of 6" requirement, but they add technical depth that judges will appreciate in the Implementation category (70 pts):

| Bonus Concept | Implementation | Scoring Impact |
|---|---|---|
| **Sessions & State Handoff** | Session state flows between agents | Strengthens "Technical Implementation" score |
| **Long-Term Memory** | Cross-session learning | Strengthens "wow factor" |
| **Observability (Traces)** | OpenTelemetry tracing | Strengthens "architecture quality" |
| **Agent Evaluation (LLM-as-Judge)** | Strategy quality scoring | Strengthens "innovation" |
| **HITL** | Strategy approval gate | Part of official concept "Agent Skills" or "Security" |

---

## Revised Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  USER: "Analyze this competition"              │
│                  Input: Competition URL / Dataset              │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT (ADK)                          │
│  • Parses intent & routes to sub-agents                       │
│  • Manages session state (context engineering)                │
│  • Enforces security (input validation, no secrets)           │
│  • HITL gate at strategy → code boundary                      │
└──┬───────────┬───────────┬───────────┬────────────────────────┘
   │           │           │           │
   ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│Scraper│  │ Data  │  │Strategy│  │ Code  │
│ Agent │  │ Agent │  │ Agent  │  │ Agent │
│       │  │       │  │        │  │       │
│Skills:│  │Skills:│  │Skills: │  │Skills:│
│•scrape│  │•profile│ │•rank   │  │•gen   │
│•search│  │•target│  │•eval   │  │•format│
└───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘
    │          │          │          │
    ▼          ▼          ▼          ▼
 [MCP Servers]  [MCP Servers]  [Session State]
 Web Scraper     Data Server    Memory Store
 File Server
```

### Concept Mapping to Architecture

| Official Concept | Where It Lives |
|---|---|
| **1. Multi-Agent (ADK)** | `agents/` — Orchestrator + 4 sub-agents |
| **2. MCP Servers** | `mcp_servers/` — 3 servers with 8+ tools |
| **3. Antigravity** | Demonstrated in **video** — show the IDE being used to build the project |
| **4. Security** | `security/` — input validation, API key safety, safe code gen |
| **5. Agent Skills** | `skills/` — modular capabilities loaded by agents (profile, rank, evaluate) |
| **HITL** | Built into orchestrator flow — strategy approval gate |
| **Sessions & Memory** | `context/` — state handoff + cross-session learning |
| **Observability** | `observability/` — OpenTelemetry traces |
| **Evaluation** | `evaluation/` — LLM-as-Judge for strategy quality |

---

## Updated Project Structure

```
kagglebot/
├── README.md                        # Comprehensive docs
├── requirements.txt
├── .env.example                     # GOOGLE_API_KEY template (no real secrets)
├── main.py                          # Entry point — orchestrator + Mesop UI
│
├── agents/                          # Official Concept 1: Multi-Agent (ADK)
│   ├── __init__.py
│   ├── orchestrator.py              # Root agent — routes + session management
│   ├── scraper_agent.py             # Competition research
│   ├── data_agent.py                # Dataset profiling
│   ├── strategy_agent.py            # ML strategy ranking
│   └── code_agent.py                # Baseline code generation
│
├── mcp_servers/                     # Official Concept 2: MCP Servers
│   ├── __init__.py
│   ├── web_scraper_server.py        # scrape_competition_page, search_discussions
│   ├── data_server.py               # load_dataset, compute_profile, analyze_target, detect_issues
│   └── file_server.py               # write_notebook, write_report
│
├── skills/                          # Official Concept 6: Agent Skills
│   ├── __init__.py
│   ├── data_profiler.py             # Reusable data profiling skill
│   ├── strategy_ranker.py           # Strategy ranking + comparison skill
│   ├── code_templates.py            # Template-based code generation skill
│   └── memory_skill.py             # Context management + memory retrieval
│
├── security/                        # Official Concept 4: Security Features
│   ├── __init__.py
│   ├── input_validator.py           # Schema validation for all MCP tool inputs
│   ├── secret_scanner.py            # Ensures no API keys in generated code
│   └── safe_code_gen.py             # Sandboxed code generation guardrails
│
├── context/                         # Bonus: Sessions & Memory
│   ├── __init__.py
│   ├── session_manager.py           # Session state schema + handoff
│   └── memory_manager.py            # Long-term memory store + retrieval
│
├── observability/                   # Bonus: Observability
│   ├── __init__.py
│   ├── tracing.py                   # OpenTelemetry setup + ADK integration
│   └── trace_viewer.py              # Trace export + terminal visualization
│
├── evaluation/                      # Bonus: Agent Evaluation
│   ├── __init__.py
│   ├── strategy_evaluator.py        # LLM-as-Judge for strategy quality
│   └── eval_criteria.py             # Rubric definitions
│
├── data/                            # Sample datasets for offline demo
│   ├── titanic_train.csv
│   └── titanic_test.csv
│
├── deployment/                      # Official Concept 5: Deployability
│   ├── Dockerfile                   # Container build config
│   ├── cloudbuild.yaml              # Cloud Run deployment config
│   ├── deploy.sh                    # One-click deploy script
│   └── README_DEPLOY.md             # Deployment guide
│
├── notebooks/                       # Kaggle Notebook export
│   └── kagglebot_demo.ipynb         # Self-contained demo notebook
│
├── output/                          # Generated outputs (gitignored)
│   ├── strategy_report.md
│   ├── baseline_notebook.py
│   └── eval_report.json
│
└── tests/
    ├── test_agents.py
    ├── test_mcp_tools.py
    ├── test_skills.py
    └── test_security.py
```

---

## Implementation Timeline (9 Days)

### Day 1 — Jun 27: Foundation + Scraper

| Task | Files | Details |
|---|---|---|
| Project scaffolding | `requirements.txt`, `.env.example`, `main.py` | ADK, MCP SDK, pandas, numpy, bs4, requests, opentelemetry |
| Orchestrator skeleton | `agents/orchestrator.py` | ADK Agent with routing logic, session state init |
| Web Scraper MCP server | `mcp_servers/web_scraper_server.py` | `scrape_competition_page(url)` and `search_discussions(url)` tools |
| Scraper Agent | `agents/scraper_agent.py` | Calls Web Scraper MCP, outputs structured competition metadata |
| **Milestone**: Scraper Agent extracts metadata from Titanic competition URL | | |

---

### Day 2 — Jun 28: Data Pipeline

| Task | Files | Details |
|---|---|---|
| Data MCP server | `mcp_servers/data_server.py` | `load_dataset`, `compute_profile`, `analyze_target`, `detect_issues` |
| Data Agent | `agents/data_agent.py` | Calls Data MCP, outputs data profile report |
| Data profiler skill | `skills/data_profiler.py` | Reusable profiling logic (stats, nulls, types, distributions) |
| Session state setup | `context/session_manager.py` | Define session state schema, wire Scraper → Data handoff |
| **Milestone**: Data Agent profiles Titanic dataset using session state from Scraper | | |

---

### Day 3 — Jun 29: Strategy + HITL

| Task | Files | Details |
|---|---|---|
| Strategy Agent | `agents/strategy_agent.py` | Reads session state (metadata + profile), generates ranked strategies |
| Strategy ranker skill | `skills/strategy_ranker.py` | Ranking logic, expected score estimation |
| HITL approval gate | Built into orchestrator | Strategy Agent output pauses for user review via ADK HITL |
| File MCP server | `mcp_servers/file_server.py` | `write_report`, `write_notebook` tools |
| **Milestone**: Full pipeline Scraper → Data → Strategy with HITL pause | | |

---

### Day 4 — Jun 30: Code Generation + Security

| Task | Files | Details |
|---|---|---|
| Code Agent | `agents/code_agent.py` | Generates baseline Python from approved strategy + profile |
| Code template skill | `skills/code_templates.py` | Template-based code gen with tested building blocks |
| Security layer | `security/input_validator.py`, `secret_scanner.py`, `safe_code_gen.py` | Input validation, no-secrets scanning, safe code generation |
| **Milestone**: Full pipeline end-to-end. Generated code runs on Titanic | | |

---

### Day 5 — Jul 1: Memory + Skills Polish

| Task | Files | Details |
|---|---|---|
| Memory system | `context/memory_manager.py`, `skills/memory_skill.py` | ADK memory service: persist learnings, retrieve in new sessions |
| Skills refinement | `skills/*.py` | Ensure all skills are modular, reusable, well-documented |
| **Milestone**: Re-analyze with modified intent works. New session retrieves past learnings | | |

---

### Day 6 — Jul 2: Observability + Evaluation

| Task | Files | Details |
|---|---|---|
| OpenTelemetry tracing | `observability/tracing.py`, `trace_viewer.py` | Trace all agent + tool calls. Export to JSON/terminal |
| Strategy evaluator | `evaluation/strategy_evaluator.py`, `eval_criteria.py` | LLM-as-Judge with 5-criterion rubric |
| **Milestone**: Traces show full pipeline timing. Evaluator scores strategies | | |

---

### Day 7 — Jul 3: UI + Deployment

| Task | Files | Details |
|---|---|---|
| Mesop chat UI | `main.py` | ADK's built-in chat UI, configured for KaggleBot |
| Dockerfile | `deployment/Dockerfile` | Multi-stage build, Python 3.11, slim image |
| Cloud Run config | `deployment/cloudbuild.yaml`, `deploy.sh` | One-click deploy script + docs |
| End-to-end testing | Multiple | Test with 3 competitions: Titanic, House Prices, Spaceship Titanic |
| Error handling | All agents | Graceful failures, cached fallbacks, user-friendly error messages |
| **Milestone**: App runs locally AND in Docker. All 3 competitions work | | |

---

### Day 8 — Jul 4: Documentation

| Task | Files | Details |
|---|---|---|
| README.md | `README.md` | Problem statement, architecture diagram, setup (<5 min), demo walkthrough, concept mapping (official 5/6), screenshots, trace screenshots |
| Code comments | All files | Ensure all modules have docstrings, key decisions documented |
| .gitignore | `.gitignore` | Exclude output/, .env, __pycache__ |
| **Milestone**: README is complete. Code is clean and commented | | |

---

### Day 9 — Jul 5: Video + Submission

| Task | Deliverable | Details |
|---|---|---|
| Record demo video | YouTube (≤ 5 min) | Script: Hook (meta angle) → Problem → Show Antigravity IDE clips → Live demo on Titanic → Show trace → Show Cloud Run deployment → Concept mapping (6/6) → Outro |
| Write Kaggle writeup | Competition submission | Problem, solution, architecture diagram, concept list (6/6), journey narrative |
| Deploy to Cloud Run | Live public URL | Run `deploy.sh`, verify live demo works |
| Push to GitHub | Public repo | Clean repo with README, .env.example, no secrets |
| Create Kaggle Notebook | `notebooks/kagglebot_demo.ipynb` | Self-contained demo that can run on Kaggle |
| Submit | Kaggle submission page | Writeup + video + all 3 links (Cloud Run + GitHub + Kaggle Notebook) |
| **Milestone**: Submitted on all 3 platforms! | | |

### Day 10 — Jul 6: Buffer

Emergency fixes only. Deadline: 11:59 PM PT.

---

## Submission Checklist

### Required Components
- [ ] **Kaggle Writeup** — problem, solution, architecture, concept mapping
- [ ] **YouTube Video** — ≤ 5 minutes, shows all 5 official concepts
- [ ] **Public Project Link** — accessible URL (GitHub repo or deployed app)
- [ ] **Media Gallery** — screenshots/diagrams attached
- [ ] **Code** — linked from writeup, no API keys

### Official Concepts Demonstrated (need ≥3, targeting ALL 6)
- [ ] ✅ **Agent / Multi-agent systems (ADK)** — 5 agents in code
- [ ] ✅ **MCP Servers** — 3 servers, 8+ tools in code
- [ ] ✅ **Antigravity** — development clips in video
- [ ] ✅ **Security features** — input validation, secret scanning in code
- [ ] ✅ **Deployability** — Dockerfile + Cloud Run deployment, shown in video
- [ ] ✅ **Agent Skills** — modular skills (profiler, ranker, templates, memory) in code

### Bonus Differentiators
- [ ] Sessions & state handoff between agents
- [ ] Long-term memory across sessions
- [ ] OpenTelemetry observability traces
- [ ] LLM-as-Judge strategy evaluation
- [ ] HITL strategy approval gate

### Platforms
- [ ] Live on **Cloud Run** with public URL
- [ ] Public **GitHub** repo with clean README
- [ ] **Kaggle Notebook** demo that runs in Kaggle environment

### Quality Gates
- [ ] Demo runs on 3+ different competitions
- [ ] No API keys in source code
- [ ] README includes setup instructions that work in < 5 minutes
- [ ] Docker build succeeds and app runs in container
- [ ] Generated baseline code actually runs
- [ ] Video is engaging and under 5 minutes

---

## Verification Plan

### Automated Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Test MCP tools individually
python -m pytest tests/test_mcp_tools.py -v

# Test security (no secrets in output)
python -m pytest tests/test_security.py -v
```

### Manual Verification
1. **End-to-end on Titanic**: Full pipeline produces strategy report + working baseline
2. **End-to-end on House Prices**: Different competition type (regression) works
3. **End-to-end on Spaceship Titanic**: Memory retrieves Titanic learnings
4. **HITL test**: Strategy step pauses for approval, modification works
5. **Security test**: Generated code contains no API keys or secrets
6. **Trace test**: Full pipeline trace is visible and exportable
7. **Evaluation test**: Strategy evaluator produces scores with reasoning

---

## Resolved Decisions

| Question | Decision |
|---|---|
| **Antigravity demonstration** | Record Antigravity IDE development clips for the video |
| **Public Project Link** | All 3 platforms: GitHub repo + Cloud Run live URL + Kaggle Notebook |
| **Deployability concept** | Dockerfile + `cloudbuild.yaml` + `deploy.sh` → full Cloud Run deployment |
