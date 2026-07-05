"""
KaggleBot — ADK Agent Configuration

This module exports the root agent for ADK to discover.
When running `adk web` or `adk run`, ADK looks for the `root_agent`
variable in the agent module.
"""

from agents.orchestrator import orchestrator_agent

# ADK discovers this as the root agent
root_agent = orchestrator_agent
