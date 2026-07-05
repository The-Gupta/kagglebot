# 🤖 KaggleBot — AI-Powered Kaggle Competition Strategy Agent

> A multi-agent system built with Google Agent Development Kit (ADK) that
> analyzes Kaggle competitions and generates complete baseline code.

Built for the **Google 5-Day Gen AI Intensive Course Capstone** to demonstrate
mastery of 6 core concepts + 5 bonus differentiators.

---

## 🎯 What It Does

Give KaggleBot a Kaggle competition URL and it:

1. **🔍 Scrapes** competition metadata and discussion insights
2. **📊 Profiles** the dataset (types, nulls, correlations, quality score)
3. **📋 Recommends** ranked ML strategies tailored to your data
4. **⏸️ Waits** for your approval (Human-in-the-Loop)
5. **💻 Generates** a complete, runnable Python baseline script
6. **🔒 Validates** generated code for security (no leaked secrets, no dangerous ops)
7. **🧠 Remembers** insights for future competitions

---

## 🏗️ Architecture

```
User
  │
  ▼
┌─────────────────────────────────────────┐
│       Orchestrator Agent (root)         │
│  memory tools: recall / store / stats  │
├─────────────────────────────────────────┤
│  ┌───────────┐  ┌────────────┐         │
│  │  Scraper   │→│   Data     │         │
│  │  Agent     │  │   Agent    │         │
│  │            │  │            │         │
│  │ Tools:     │  │ Tools:     │         │
│  │ - scrape   │  │ - load     │         │
│  │ - discuss  │  │ - profile  │         │
│  └───────────┘  │ - target   │         │
│                 │ - issues   │         │
│                 └────────────┘         │
│                      │                  │
│                      ▼                  │
│  ┌───────────┐  ┌────────────┐         │
│  │ Strategy   │→│   Code     │         │
│  │ Agent      │  │   Agent    │         │
│  │            │  │            │         │
│  │ ⏸️ HITL    │  │ Tools:     │         │
│  │ approval   │  │ - generate │         │
│  │ gate       │  │ - save     │         │
│  └───────────┘  │ 🔒 security│         │
│                 └────────────┘         │
└─────────────────────────────────────────┘
```

### Data Flow via Session State

```
Scraper → session["competition_metadata"]
Data    → session["data_profile"]
Strategy → session["strategies"] → HITL → session["approved_strategy"]
Code    → session["generated_code"]
```

---

## 🧩 Concepts Demonstrated

### Core Concepts (Required)

| # | Concept | Where | Description |
|---|---------|-------|-------------|
| 1 | **ADK (Multi-Agent)** | `agents/*.py` | 5-agent system: Orchestrator + Scraper + Data + Strategy + Code |
| 2 | **MCP Servers** | `mcp_servers/*.py` | 3 servers: Web Scraper (2 tools), Data (4 tools), File (2 tools) |
| 3 | **Antigravity** | Built in Antigravity IDE | Development recorded for demo video |
| 4 | **Security** | `security/*.py` | Input validation, secret scanning, AST-based code safety |
| 5 | **Deployability** | `deployment/` | Dockerfile + Cloud Run config + deploy script |
| 6 | **Agent Skills** | `skills/*.py` | 4 modular skills: data profiler, strategy ranker, code templates, memory |

### Bonus Differentiators

| # | Concept | Where | Description |
|---|---------|-------|-------------|
| 7 | **Observability** | `observability/*.py` | OpenTelemetry-inspired tracing with hierarchical tree visualization |
| 8 | **Evaluation** | `evaluation/*.py` | LLM-as-Judge with 5-criterion rubric and weighted scoring |
| 9 | **Memory** | `context/memory_manager.py` | Cross-session persistent learning with relevance scoring |
| 10 | **Sessions** | `context/session_manager.py` | Agent-to-agent data flow via session state keys |
| 11 | **HITL** | Strategy Agent | Mandatory user approval before code generation |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Google Gemini API key](https://aistudio.google.com/apikey)
- [Google ADK](https://google.github.io/adk-docs/) (`pip install google-adk`)

### Setup

```bash
# Clone the repo
git clone https://github.com/The-Gupta/kagglebot.git
cd kagglebot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run with ADK Web UI

```bash
adk web
```

Then open `http://localhost:8000` and try:

> Analyze this Kaggle competition: https://www.kaggle.com/competitions/titanic

### Run Tests (No API Key Required)

```bash
python tests/test_e2e.py
```

---

## 📁 Project Structure

```
kagglebot/
├── agent.py                    # ADK root agent config
├── main.py                     # Entry point
├── requirements.txt
│
├── agents/                     # Multi-Agent System
│   ├── orchestrator.py         # Root agent (coordinator)
│   ├── scraper_agent.py        # Competition researcher
│   ├── data_agent.py           # Dataset profiler
│   ├── strategy_agent.py       # ML strategist (with HITL)
│   └── code_agent.py           # Code generator
│
├── mcp_servers/                # MCP Tool Servers
│   ├── web_scraper_server.py   # Scrape competitions + discussions
│   ├── data_server.py          # Load, profile, analyze datasets
│   └── file_server.py          # Write reports + notebooks
│
├── skills/                     # Reusable Agent Skills
│   ├── data_profiler.py        # Full dataset profiling
│   ├── strategy_ranker.py      # Strategy templates + ranking
│   ├── code_templates.py       # ML code generation templates
│   └── memory_skill.py         # Long-term memory tools
│
├── security/                   # Security Features
│   ├── input_validator.py      # URL, path, column validation
│   ├── secret_scanner.py       # API key / token detection
│   └── safe_code_gen.py        # AST-based code safety analysis
│
├── context/                    # State Management
│   ├── session_manager.py      # Session state key definitions
│   └── memory_manager.py       # Persistent memory store
│
├── observability/              # Tracing & Monitoring
│   ├── tracing.py              # OpenTelemetry-inspired spans
│   └── trace_viewer.py         # Tree visualization + HTML export
│
├── evaluation/                 # Quality Assessment
│   ├── eval_criteria.py        # 5-criterion evaluation rubric
│   └── strategy_evaluator.py   # LLM-as-Judge evaluator
│
├── deployment/                 # Cloud Deployment
│   ├── Dockerfile              # Production container
│   ├── cloudbuild.yaml         # Cloud Build CI/CD
│   └── deploy.sh               # One-command deploy script
│
├── data/                       # Sample datasets
│   └── titanic_train.csv       # Titanic sample (100 rows)
│
├── output/                     # Generated artifacts
│   └── traces/                 # Trace JSON files
│
└── tests/                      # Test suite
    └── test_e2e.py             # Comprehensive E2E tests
```

---

## 🔒 Security Features

1. **Input Validation** — All URLs validated as Kaggle domains; file paths checked for traversal attacks
2. **Secret Scanning** — Generated code scanned for 10+ secret patterns (API keys, tokens, passwords, AWS keys)
3. **Safe Code Generation** — AST parsing blocks dangerous operations (shell exec, file deletion, network requests)
4. **Import Blocking** — Prevents generated code from importing `subprocess`, `shutil`, `socket`, `pickle`
5. **Auto-Sanitization** — Unsafe code is commented out, not silently passed through

---

## 📊 Observability

KaggleBot produces structured traces showing the full pipeline execution:

```
[Trace: titanic-analysis-abc123]
└── 🤖 kagglebot_orchestrator (197ms) ✅
    ├── 🔧 recall_learnings (12ms) ✅
    ├── 🤖 scraper_agent (35ms) ✅
    │   ├── 🔧 scrape_competition_page (22ms) ✅
    │   └── 🔧 search_discussions (13ms) ✅
    ├── 🤖 data_agent (47ms) ✅
    │   ├── 🔧 load_and_preview (12ms) ✅
    │   ├── 🔧 profile_dataset (23ms) ✅
    │   └── 🔧 analyze_target_variable (12ms) ✅
    ├── 🤖 strategy_agent (68ms) ✅
    │   ├── 🔧 generate_strategies (12ms) ✅
    │   └── ⏸️ user_approval (55ms) ✅
    └── 🤖 code_agent (34ms) ✅
        ├── 🔧 generate_baseline_code (22ms) ✅
        └── 🔧 security_check (12ms) ✅
```

---

## 🚢 Deployment

### Local Docker

```bash
docker build -t kagglebot -f deployment/Dockerfile .
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key kagglebot
```

### Cloud Run

```bash
export GOOGLE_API_KEY=your_key
./deployment/deploy.sh
```

---

## 📝 License

MIT License. Built for the Google 5-Day Gen AI Intensive Course Capstone 2025.
