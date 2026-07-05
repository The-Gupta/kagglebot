# KaggleBot — Build Walkthrough

## What Was Built

**KaggleBot** is a multi-agent system built with Google ADK that analyzes Kaggle competitions and generates baseline ML code. It demonstrates **11 concepts** from the Google Gen AI Intensive Course.

## Architecture

```
User → Orchestrator (root) → Scraper Agent → Data Agent → Strategy Agent → [HITL] → Code Agent
                ↕ memory tools
```

## Components Built (by Day)

### Day 1: Foundation + Scraper
- Project scaffolding, ADK config, session manager
- Web Scraper MCP server (cached data for 3 competitions)
- Scraper Agent with 2 tools

### Day 2: Data Pipeline
- Data MCP server with 4 tools (load, profile, target, issues)
- Data Agent with session state handoff
- Data profiler skill
- Sample Titanic CSV (100 rows)

### Day 3: Strategy + HITL
- Strategy ranker skill (templates for 3 competition types)
- Strategy Agent with HITL approval gate (4 tools)
- File MCP server (write_report, write_notebook)

### Day 4: Code Generation + Security
- Code templates skill (171-line baseline generator)
- Code Agent with 3 tools + integrated security
- Input validator (URL, path, column validation)
- Secret scanner (10+ patterns, redaction)
- Safe code gen (AST-based, import blocking, sanitization)

### Day 5: Memory + Skills Polish
- Memory manager (JSON-backed persistent storage)
- Memory skill (store/recall/stats)
- Orchestrator updated with memory tools

### Day 6: Observability + Evaluation
- OpenTelemetry-inspired tracing (Span/Tracer)
- Trace viewer (tree rendering, HTML export)
- Strategy evaluator (LLM-as-Judge pattern)
- Eval criteria (5-criterion rubric, weighted scoring)

### Day 7: Deployment + E2E Testing
- Dockerfile (python:3.12-slim, health check)
- Cloud Run config + deploy script
- E2E test suite: **7/7 passed, 0 failed (1.54s)**

### Day 8: Documentation
- README.md (255 lines — architecture, concepts, quick start)
- Deployment guide (local, Docker, Cloud Run)
- Finalized .gitignore

### Day 9: Notebook + Submission Prep
- Demo notebook running all 11 concepts without API key

## Validation Results

- ✅ All Python imports work
- ✅ 7/7 E2E tests pass (1.54s)
- ✅ Security: blocks non-Kaggle URLs, path traversal, secrets in code
- ✅ Generated code passes AST safety analysis
- ✅ Memory relevance scoring works correctly
- ✅ Trace tree renders with 15 spans across 5 agents
- ✅ Evaluation weighted score: 4.1/5.0
- ✅ Demo notebook runs end-to-end without API key

## Final Stats

| Metric | Value |
|--------|-------|
| Total files | 43 |
| Python files | 32 |
| Lines of code | 5,239 |
| Agents | 5 |
| MCP tools | 8 |
| Skills | 4 |
| Security checks | 3 |
| E2E tests | 7/7 |
| Concepts | 11 (6 core + 5 bonus) |
