# KaggleBot — Kaggle Competition Strategy Agent

## Track: Agents for Business

## Submission Deadline: July 6, 2026, 11:59 PM PT

---

## 1. Problem Statement

### The Pain Point

When a data scientist joins a Kaggle competition, the first **4–8 hours** are spent on repetitive discovery work before any real modeling begins:

1. **Reading and parsing** the competition overview, evaluation metric, data description, and rules
2. **Downloading and profiling** the dataset — schema, types, distributions, nulls, cardinality, target variable analysis
3. **Scouring the Discussion tab** for winning strategies, common pitfalls, and starter notebooks from past similar competitions
4. **Mentally synthesizing** all of this into a ranked strategy — *"Should I try gradient boosting first or a neural net? Is feature engineering or ensembling more important here?"*
5. **Writing boilerplate** — baseline code for loading, preprocessing, cross-validation, and submission formatting

This is **high-value work**, but it's predictable and pattern-driven — exactly the kind of work an AI agent should automate.

### The Opportunity

> *"Analyze the Titanic competition and give me a ranked strategy with a baseline notebook."*

One sentence. The agent reads the competition, profiles the data, researches winning approaches, and delivers a complete strategy document with working starter code — all in minutes, not hours.

### Why This Wins

- **Meta appeal** — A Kaggle agent, submitted on Kaggle, judged by Kaggle staff. The self-referential cleverness is memorable.
- **Zero competition** — No existing capstone submission does this (verified across ~50 entries).
- **Instantly demo-able** — Point it at *any* public competition and it produces useful output.
- **Genuine business value** — Data science consulting teams, competitive ML labs, and Kaggle teams could actually use this.

---

## 2. Proposed Solution: KaggleBot

A **multi-agent system** built with Google ADK that acts as an AI-powered Kaggle competition analyst. Given a competition URL, it orchestrates specialized agents to research, analyze, strategize, and generate code — delivering a complete competition playbook.

### Core Value Proposition

> Compress 4–8 hours of competition discovery into a 5-minute automated analysis, producing a ranked strategy and baseline code that would take an experienced Kaggler a full day to assemble.

---

## 3. Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                  USER: "Analyze this competition"              │
│                  Input: Competition URL / Dataset              │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT (ADK)                      │
│  • Parses user intent & competition URL                       │
│  • Manages session state & conversation memory                │
│  • Routes to specialized agents in logical order              │
│  • Aggregates results into final strategy document            │
└──┬───────────┬───────────┬───────────┬────────────────────────┘
   │           │           │           │
   ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│Scraper│  │ Data  │  │  Strat │  │ Code  │
│ Agent │  │ Agent │  │  Agent │  │ Agent │
└───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘
    │          │          │          │
    ▼          ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│  MCP  │  │  MCP  │  │Session│  │Session│
│Server │  │Server │  │& Mem. │  │& Mem. │
└───────┘  └───────┘  └───────┘  └───────┘
    │          │          │          │
    └──────────┴──────┬───┴──────────┘
                      │
              ┌───────┴────────┐
              │  OBSERVABILITY │  ← Concept 5: Structured logs
              │  (Logs/Traces) │     & traces across all agents
              └───────┬────────┘
                      │
              ┌───────┴────────┐
              │   EVALUATION   │  ← Concept 6: LLM-as-Judge
              │ (Quality Gate) │     scores strategy quality
              └────────────────┘
```

---

## 4. Key Concepts Demonstrated (6 — Covering Days 1–4)

### Concept Coverage by Day

| Day | Concept | Role in KaggleBot |
|---|---|---|
| **Day 1** | Multi-Agent Systems (ADK) | Core architecture — 4 specialized agents + orchestrator |
| **Day 2** | MCP Servers | Tool layer — web scraping, data profiling, file I/O |
| **Day 2** | Human-in-the-Loop (HITL) | Safety gate — user approves strategy before code generation |
| **Day 3** | Sessions & Memory | State handoff between agents; cross-session learning |
| **Day 4** | Observability (Logs & Traces) | Structured tracing across the full agent pipeline |
| **Day 4** | Agent Evaluation | LLM-as-Judge scores strategy quality for continuous improvement |

> [!TIP]
> **6 concepts across 4 days** gives comprehensive course coverage. Most submissions only demonstrate 3. The Day 4 concepts (observability + evaluation) are especially rare in submissions — they signal production-readiness and engineering maturity that judges will notice.

---

### Concept 1: Multi-Agent Systems (ADK)

| Agent | Role | Input | Output |
|---|---|---|---|
| **Orchestrator** | Coordinator & conversation manager | User request + competition URL | Final strategy document |
| **Scraper Agent** | Competition researcher | Competition URL | Structured competition metadata (description, metric, rules, deadlines, past winner summaries) |
| **Data Agent** | Data analyst | Dataset file(s) | Data profile report (schema, statistics, quality issues, target analysis, feature insights) |
| **Strategy Agent** | ML strategist | Competition metadata + data profile | Ranked list of approaches with reasoning, estimated leaderboard ranges, and risk assessments |
| **Code Agent** | Baseline generator | Approved strategy + data profile | Working Python notebook: load → preprocess → train → validate → submit |

**Agent Coordination Flow:**
```
Scraper Agent → outputs competition metadata
                    ↓
Data Agent → outputs data profile (uses metadata for context)
                    ↓
Strategy Agent → outputs ranked strategies (uses both above)
                    ↓
    [HITL: User reviews/approves/modifies strategy]
                    ↓
Code Agent → outputs baseline notebook (uses approved strategy + profile)
```

Each agent is **sequential and builds on prior agent outputs** — this is an intentional design choice. It mirrors how an experienced Kaggler actually works: read the problem → look at the data → form a strategy → write code. This makes the demo narrative intuitive.

---

### Concept 2: MCP Servers

MCP servers expose tools that agents use to interact with the real world.

| MCP Server | Tools | Used By |
|---|---|---|
| **Web Scraper MCP** | `scrape_competition_page` — fetches and parses competition overview, evaluation, data description, rules | Scraper Agent |
| | `search_discussions` — retrieves top discussion posts (tips, winning solutions, common mistakes) | Scraper Agent |
| **Data MCP** | `load_dataset` — loads CSV/Parquet into memory, returns shape and first rows | Data Agent |
| | `compute_profile` — generates column-level statistics (dtype, nulls, unique, mean, std, distribution) | Data Agent |
| | `analyze_target` — class balance, distribution, correlation with features | Data Agent |
| | `detect_issues` — flags data quality issues (high cardinality, constant columns, leakage suspects) | Data Agent |
| **File MCP** | `write_notebook` — writes generated Python code as a .py or .ipynb file | Code Agent |
| | `write_report` — writes the strategy document as Markdown | Strategy Agent |

**Why MCP?** Agents reason about *what* to do; MCP servers handle *how*. This separation means:
- The Scraper Agent doesn't know about `requests` or `BeautifulSoup` — it just calls `scrape_competition_page(url)`
- Tools can be improved independently (e.g., swap `BeautifulSoup` for `Playwright`) without touching agent logic

---

### Concept 3: Sessions & Memory (Context Engineering)

This is KaggleBot's **secret weapon** — most capstone entries are stateless one-shot demos. KaggleBot uses ADK's session and memory systems to enable:

#### Sessions (Short-Term — Within a Conversation)
- Each analysis run creates a **session** that accumulates structured state:
  ```
  session.state = {
      "competition_metadata": { ... },   # From Scraper Agent
      "data_profile": { ... },           # From Data Agent
      "strategies": [ ... ],             # From Strategy Agent
      "approved_strategy": { ... },      # After HITL approval
      "generated_code": "..."            # From Code Agent
  }
  ```
- Agents **read from and write to session state**, enabling seamless handoff
- Users can ask follow-up questions: *"What if I focus on ensembling instead?"* — the Strategy Agent re-ranks using the existing session context without re-running prior agents

#### Memory (Long-Term — Across Conversations)
- When a user completes an analysis, key learnings are persisted to **long-term memory**:
  - Competition type patterns (e.g., "tabular binary classification → try LightGBM first")
  - User's preferred frameworks (e.g., "user prefers PyTorch over TensorFlow")
  - Past competition strategies and their outcomes
- On subsequent analyses, the Orchestrator retrieves relevant memories:
  *"You analyzed a similar tabular classification competition last week and LightGBM with target encoding scored highest. Apply similar approach?"*

#### Demo Scenario
```
User: "Analyze the Titanic competition"
→ Full analysis runs, strategy generated

User: "Actually, focus more on feature engineering approaches"
→ Strategy Agent re-ranks using existing session state (no re-scraping or re-profiling)

[New session, days later]
User: "Analyze the Spaceship Titanic competition"
→ Memory retrieves: "Similar to Titanic (tabular binary classification).
   Previously, tree-based models with careful feature engineering worked best."
→ Strategy Agent incorporates this prior knowledge
```

---

### Concept 4: Human-in-the-Loop (HITL)

HITL is critical at the **Strategy → Code** boundary. The agent should never auto-generate code for a strategy the user hasn't reviewed.

#### Where HITL Is Applied

| Checkpoint | What Happens | Why |
|---|---|---|
| **Strategy Review** | Strategy Agent presents ranked approaches; user approves, modifies, or requests alternatives before Code Agent runs | The user's judgment is irreplaceable — they know their compute budget, time constraints, and domain expertise |
| **Code Review** | Generated baseline is presented for review; user can request modifications | Prevents blindly running auto-generated code |
| **Data Quality Alerts** | If Data Agent finds critical issues (potential target leakage, severe class imbalance), analysis pauses for user acknowledgment | Prevents building models on flawed data assumptions |

#### Implementation
- ADK's built-in HITL mechanism: agent yields a **pending action** that pauses execution
- User reviews in the chat UI and responds with approval/modification
- Agent resumes with user's decision incorporated

---

### Concept 5: Observability (Logs & Traces)

With 4 agents chaining outputs, debugging failures or understanding bottlenecks is critical. Observability provides **full visibility** into the agent pipeline.

#### What We Trace

| Trace Element | What It Captures | Value |
|---|---|---|
| **Agent Spans** | Start/end time, agent name, input summary, output summary for each agent | See which agent took longest; identify bottlenecks |
| **Tool Call Spans** | Each MCP tool invocation with arguments and return values | Debug tool failures; verify correct tool usage |
| **LLM Call Spans** | Token counts, latency, prompt/response summaries | Monitor cost and latency per agent |
| **Session State Writes** | What each agent added to session state | Verify correct data handoff between agents |
| **HITL Events** | When execution paused, what the user decided, resume time | Understand user interaction patterns |

#### Implementation
- **OpenTelemetry** integration via ADK's built-in tracing support
- Traces exported to **JSON** for easy visualization and sharing
- A lightweight `trace_viewer.py` utility renders traces as a timeline in the terminal or exports to HTML
- Every agent run produces a trace ID that can be inspected after completion

#### Demo Value
In the video demo, showing a **trace visualization** of the full pipeline is extremely compelling:
```
[Trace: analyze-titanic-001]
├── Orchestrator (total: 45.2s)
│   ├── Scraper Agent (8.1s)
│   │   ├── scrape_competition_page (3.2s) ✅
│   │   └── search_discussions (4.9s) ✅
│   ├── Data Agent (12.3s)
│   │   ├── load_dataset (0.5s) ✅
│   │   ├── compute_profile (6.1s) ✅
│   │   ├── analyze_target (3.2s) ✅
│   │   └── detect_issues (2.5s) ✅
│   ├── Strategy Agent (15.8s)
│   │   ├── LLM reasoning (14.2s) — 2,100 tokens
│   │   └── write_report (1.6s) ✅
│   ├── [HITL Pause] (user review: 30s)
│   └── Code Agent (9.0s)
│       ├── LLM code generation (7.8s) — 3,400 tokens
│       └── write_notebook (1.2s) ✅
```

> This is the kind of slide that makes judges pause and say "this person built something real."

---

### Concept 6: Agent Evaluation (LLM-as-Judge)

How do you know if the Strategy Agent's recommendations are *good*? You can't ship an agent without a quality signal. Agent Evaluation closes this loop.

#### Evaluation Approach: LLM-as-Judge

After the Strategy Agent generates ranked strategies, a **separate evaluation step** scores the output against a defined rubric using a different LLM call (or the same LLM with a judge-specific prompt).

#### Evaluation Rubric

| Criterion | Weight | What It Measures | Score Range |
|---|---|---|---|
| **Relevance** | 25% | Do the strategies match the competition type and metric? | 1–5 |
| **Feasibility** | 25% | Are the strategies achievable given the dataset size and complexity? | 1–5 |
| **Ranking Quality** | 20% | Is the #1 strategy genuinely the best starting point? | 1–5 |
| **Completeness** | 15% | Does the strategy cover preprocessing, modeling, validation, and submission? | 1–5 |
| **Novelty** | 15% | Does it go beyond "just use XGBoost"? Any creative feature engineering or ensembling ideas? | 1–5 |

#### How It Works
```
Strategy Agent Output → Strategy Evaluator (LLM-as-Judge)
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Evaluation Report   │
                    │ Relevance:    4/5   │
                    │ Feasibility:  5/5   │
                    │ Ranking:      4/5   │
                    │ Completeness: 3/5   │
                    │ Novelty:      3/5   │
                    │ Overall:      3.9/5 │
                    │                     │
                    │ Feedback: "Consider │
                    │ adding an ensembling│
                    │ strategy for the    │
                    │ advanced tier."     │
                    └─────────────────────┘
```

#### Why This Matters for Winning
- Shows you care about **quality, not just output** — a production mindset
- The evaluation report can be shown in the demo as a "confidence score" for the strategy
- If the score is below a threshold, the agent can **auto-retry** with the feedback — demonstrating self-improvement
- Judges evaluating 100+ submissions will appreciate a project that *evaluates itself*

---

## 5. End-to-End Demo Walkthrough

### Primary Demo: Titanic Competition Analysis

```
User: "Analyze https://www.kaggle.com/competitions/titanic"

🔍 Scraper Agent:
   ├── Competition: Titanic - Machine Learning from Disaster
   ├── Type: Binary Classification
   ├── Metric: Accuracy
   ├── Dataset: 891 training rows, 418 test rows
   └── Key insight from discussions: Feature engineering is king;
       top solutions use family size, title extraction, cabin deck

📊 Data Agent:
   ├── 12 columns, 891 rows
   ├── Target: Survived (0/1), 38.4% survival rate
   ├── Missing: Age (19.9%), Cabin (77.1%), Embarked (0.2%)
   ├── Key features: Sex (strong predictor), Pclass, Fare
   ├── ⚠️ Cabin has 77% missing — impute or drop?
   └── 💡 Name contains extractable titles (Mr, Mrs, Master, etc.)

📋 Strategy Agent (Ranked):
   ┌─────────────────────────────────────────────────────────┐
   │ Rank │ Approach              │ Expected │ Effort │ Risk │
   │──────│───────────────────────│──────────│────────│──────│
   │  1   │ LightGBM + feature    │ 0.79-0.81│ Medium │ Low  │
   │      │ engineering (titles,  │          │        │      │
   │      │ family size, deck)    │          │        │      │
   │  2   │ Stacked ensemble      │ 0.80-0.83│ High   │ Med  │
   │      │ (RF + XGB + LR)      │          │        │      │
   │  3   │ Neural net (tabular)  │ 0.76-0.80│ High   │ High │
   └─────────────────────────────────────────────────────────┘

   ⏸️ [HITL] Do you approve Strategy #1, or would you like to modify?

User: "Go with strategy 1, but also add fare binning"

💻 Code Agent:
   → Generates complete baseline notebook:
     • Data loading + preprocessing
     • Feature engineering (title extraction, family size, fare bins)
     • LightGBM training with 5-fold CV
     • Prediction on test set
     • Submission file generation
   → Saves to: kaggle_titanic_baseline.py
```

---

## 6. Technical Stack

| Component | Technology | Rationale |
|---|---|---|
| **Agent Framework** | Google ADK | Course requirement; excellent multi-agent support |
| **LLM** | Gemini 2.0 Flash | Fast, cost-effective, good for structured reasoning |
| **Language** | Python 3.11+ | Standard for DS/ML |
| **MCP Implementation** | MCP Python SDK | Standardized tool protocol |
| **Web Scraping** | `requests` + `BeautifulSoup4` | Lightweight, no browser needed for Kaggle's SSR pages |
| **Data Processing** | Pandas, NumPy | Standard DS stack |
| **Session Storage** | ADK InMemorySessionService | Simple, demo-appropriate |
| **Memory Storage** | ADK InMemoryMemoryService | Persistent across sessions |
| **Frontend** | Mesop (ADK's built-in UI) | Zero-config chat UI, native ADK integration |

---

## 7. Deliverables (Aligned to Judging Rubric)

### The Pitch — Problem, Solution, Value (30 pts)

| Criterion | Points | Our Approach |
|---|---|---|
| **Core Concept & Value** | 10 | Crystal clear: "4–8 hours of competition research → 5 minutes." Meta angle (Kaggle agent on Kaggle) is memorable |
| **YouTube Video** (≤ 5 min) | 10 | Hook (the meta angle) → Problem → Architecture → Live demo on Titanic → Show trace visualization → Concepts demonstrated → Outro |
| **Writeup** | 10 | Structured Kaggle writeup with embedded architecture diagram, concept mapping, and journey narrative |

### The Implementation — Architecture, Code (70 pts)

| Criterion | Points | Our Approach |
|---|---|---|
| **Technical Implementation** | 50 | 4 specialized agents, 3 MCP servers with 8+ tools, session state handoff, memory, HITL, structured tracing, LLM-based evaluation. **6 course concepts across 4 days** — maximum breadth with depth |
| **Documentation** | 20 | Comprehensive README with: problem statement, architecture diagram, setup (< 5 min), demo walkthrough, concepts mapped to code, trace screenshots |

---

## 8. Project Structure

```
kagglebot/
├── README.md                        # Comprehensive docs (20 pts)
├── requirements.txt                 # Dependencies
├── .env.example                     # GOOGLE_API_KEY template
├── main.py                          # Entry point — starts orchestrator + Mesop UI
│
├── agents/                          # Concept 1: Multi-Agent System (ADK)
│   ├── __init__.py
│   ├── orchestrator.py              # Root agent — manages flow + session state
│   ├── scraper_agent.py             # Competition research
│   ├── data_agent.py                # Dataset profiling
│   ├── strategy_agent.py            # ML strategy ranking
│   └── code_agent.py                # Baseline code generation
│
├── mcp_servers/                     # Concept 2: MCP Servers
│   ├── __init__.py
│   ├── web_scraper_server.py        # Competition page + discussion scraping
│   ├── data_server.py               # Dataset loading, profiling, issue detection
│   └── file_server.py               # Notebook/report writing
│
├── context/                         # Concept 3: Sessions & Memory
│   ├── __init__.py
│   ├── session_manager.py           # Session state schema + management
│   └── memory_manager.py            # Long-term memory storage + retrieval
│
├── hitl/                            # Concept 4: Human-in-the-Loop
│   ├── __init__.py
│   └── approval_gates.py            # Strategy approval, code review, data alerts
│
├── observability/                   # Concept 5: Observability
│   ├── __init__.py
│   ├── tracing.py                   # OpenTelemetry trace setup + ADK integration
│   └── trace_viewer.py              # Utility to export/visualize traces
│
├── evaluation/                      # Concept 6: Agent Evaluation
│   ├── __init__.py
│   ├── strategy_evaluator.py        # LLM-as-Judge for strategy quality
│   ├── eval_criteria.py             # Rubric definitions (relevance, feasibility, etc.)
│   └── eval_report.py              # Generates evaluation summary report
│
├── data/                            # Sample datasets for offline demo
│   ├── titanic_train.csv
│   └── titanic_test.csv
│
├── output/                          # Generated outputs (gitignored)
│   ├── strategy_report.md
│   ├── baseline_notebook.py
│   └── eval_report.json             # Evaluation scores
│
└── tests/
    ├── test_agents.py
    ├── test_mcp_tools.py
    ├── test_session_memory.py
    └── test_evaluation.py
```

---

## 9. Timeline (9 Days Remaining)

| Day | Date | Focus | Deliverable |
|---|---|---|---|
| **1** | Jun 27 | Foundation | ADK project setup, Orchestrator + Scraper Agent + Web MCP server working. Can scrape a competition page |
| **2** | Jun 28 | Data pipeline | Data Agent + Data MCP server. Can load and profile a dataset end-to-end |
| **3** | Jun 29 | Strategy + HITL | Strategy Agent with session state + HITL approval gate. Full pipeline through strategy step |
| **4** | Jun 30 | Code gen + Memory | Code Agent generates baseline from approved strategy. Memory system for cross-session learning |
| **5** | Jul 1 | Observability | OpenTelemetry tracing across all agents. Trace export/visualization |
| **6** | Jul 2 | Evaluation + UI | LLM-as-Judge strategy evaluator. Mesop chat UI. End-to-end flow polished |
| **7** | Jul 3 | Testing + edge cases | Test with 3+ different competitions. Fix edge cases. Code cleanup |
| **8** | Jul 4 | Documentation | README.md, architecture diagrams, setup guide, trace screenshots |
| **9** | Jul 5 | Video + submission | Record YouTube demo (≤ 5 min), write Kaggle writeup, submit |
| **Buffer** | Jul 6 | Emergency | Final fixes before 11:59 PM PT deadline |

---

## 10. Success Criteria

- [ ] Scraper Agent extracts structured metadata from any public Kaggle competition URL
- [ ] Data Agent produces a complete profile report from CSV/Parquet input
- [ ] Strategy Agent generates ranked approaches with reasoning, using session state from prior agents
- [ ] HITL gate pauses execution and waits for user approval at strategy step
- [ ] Code Agent generates a runnable baseline Python script from the approved strategy
- [ ] Session state persists across the full agent pipeline (scraper → data → strategy → code)
- [ ] Memory persists key learnings and is retrieved in subsequent sessions
- [ ] Traces capture the full agent pipeline with timing and tool call details
- [ ] Strategy evaluator produces quality scores with reasoning
- [ ] Demo runs successfully on at least 3 different competitions (Titanic, House Prices, one more)
- [ ] No API keys in source code
- [ ] Demo video ≤ 5 minutes, covers all 6 concepts
- [ ] README includes problem, architecture, setup, walkthrough, concept mapping, and trace screenshots

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Kaggle page scraping blocked/rate-limited | Scraper Agent fails | Include cached HTML for demo competitions; graceful fallback to manual input |
| Generated code has bugs | Code Agent output doesn't run | Template-based generation with tested building blocks; present as "starter code" not "production code" |
| Memory retrieval is noisy | Irrelevant memories surface | Use structured memory keys (competition type, data shape) not free-text; keep memory store small |
| Scope creep | Miss deadline | Every feature maps to judging criteria. If behind schedule, cut memory (Day 5) — it's a differentiator but not required |
| Gemini API rate limits | Agent pipeline stalls | Use Gemini Flash (higher rate limits), add retry logic, cache LLM responses for demo |

> [!IMPORTANT]
> **Scope priority if time-constrained** (cut from bottom first):
> 1. Multi-Agent Systems — **must have** (core)
> 2. MCP Servers — **must have** (tools)
> 3. Sessions — **must have** (state handoff)
> 4. HITL — **must have** (safety)
> 5. Observability — **should have** (differentiator)
> 6. Agent Evaluation — **nice to have** (extra credit)
> 7. Memory — **nice to have** (impressive but cuttable)
>
> Items 1–4 are a strong entry. Adding 5 makes it competitive. Adding 5+6 makes it a top contender. Adding all 7 is the full vision.
