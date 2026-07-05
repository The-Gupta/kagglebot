"""
KaggleBot — Main Entry Point

An AI-powered Kaggle competition analyst built with Google ADK.
Orchestrates specialized agents to research, analyze, strategize,
and generate code for Kaggle competitions.

Usage:
    # Run with ADK web UI
    adk web

    # Or run programmatically
    python main.py

Concepts Demonstrated:
    1. Multi-Agent Systems (ADK) — Orchestrator + 4 sub-agents
    2. MCP Servers — Web scraping, data profiling, file I/O tools
    3. Antigravity — Built using Antigravity IDE
    4. Security — Input validation, secret scanning, safe code gen
    5. Deployability — Dockerfile + Cloud Run config
    6. Agent Skills — Modular, reusable capability modules
"""

import os
import sys

from dotenv import load_dotenv


def main():
    """Start KaggleBot with the ADK web interface."""
    # Load environment variables
    load_dotenv()

    # Verify API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("=" * 60)
        print("ERROR: GOOGLE_API_KEY not set!")
        print()
        print("Please set your Gemini API key:")
        print("  1. Copy .env.example to .env")
        print("  2. Replace 'your_gemini_api_key_here' with your key")
        print("  3. Get a key at: https://aistudio.google.com/apikey")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("  🤖 KaggleBot — Kaggle Competition Strategy Agent")
    print("=" * 60)
    print()
    print("  Starting ADK web interface...")
    print("  Run: adk web")
    print()
    print("  Or use the agent programmatically:")
    print("  >>> from agents.orchestrator import orchestrator_agent")
    print()

    # Import here to avoid issues when running tests
    from agents.orchestrator import orchestrator_agent  # noqa: F401

    print(f"  Agent '{orchestrator_agent.name}' loaded successfully!")
    print(f"  Sub-agents: {[a.name for a in orchestrator_agent.sub_agents]}")
    print()
    print("  To start the web UI, run:")
    print("    adk web")
    print()


if __name__ == "__main__":
    main()
