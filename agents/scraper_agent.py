"""
Scraper Agent — Competition researcher that extracts structured metadata.

This agent is the first in the pipeline. Given a Kaggle competition URL,
it scrapes the competition page and discussion posts, then writes
structured metadata to the session state for downstream agents.

Concept demonstrated: Multi-Agent Systems (ADK) — Specialized sub-agent
with a focused role and toolset.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from mcp_servers.web_scraper_server import (
    get_known_competition,
    scrape_competition_page,
    search_discussions,
)
from context.session_manager import SESSION_KEYS


def _scrape_competition(url: str, tool_context: ToolContext) -> dict:
    """
    Scrapes a Kaggle competition page and stores metadata in session state.

    Tries cached data first (for demo reliability), then falls back to
    live scraping. Writes the result to session state for downstream agents.

    Args:
        url: Kaggle competition URL
            (e.g., 'https://www.kaggle.com/competitions/titanic')

    Returns:
        Structured competition metadata including title, description,
        evaluation metric, data description, and inferred competition type.
    """
    import re

    # Extract slug for cache lookup
    match = re.search(r"kaggle\.com/(?:competitions|c)/([^/?\s]+)", url)
    slug = match.group(1) if match else url

    # Try cached data first (reliable for demos)
    cached = get_known_competition(slug)
    if cached:
        metadata = dict(cached)  # Copy to avoid mutation
        # Add discussion insights as part of metadata
        metadata["source"] = "cached"
    else:
        # Live scraping
        metadata = scrape_competition_page(url)
        metadata["source"] = "scraped"

    # Store in session state for downstream agents
    tool_context.state[SESSION_KEYS["competition_metadata"]] = metadata

    return metadata


def _search_competition_discussions(
    url: str, tool_context: ToolContext
) -> dict:
    """
    Searches competition discussions for tips, strategies, and insights.

    Args:
        url: Kaggle competition URL

    Returns:
        Discussion posts with titles, summaries, and key insights.
    """
    import re

    # Extract slug for cache lookup
    match = re.search(r"kaggle\.com/(?:competitions|c)/([^/?\s]+)", url)
    slug = match.group(1) if match else url

    # Try cached insights first
    cached = get_known_competition(slug)
    if cached and "discussion_insights" in cached:
        result = {
            "posts": cached["discussion_insights"],
            "total_found": len(cached["discussion_insights"]),
            "source": "cached",
        }
    else:
        # Live scraping
        result = search_discussions(url)
        result["source"] = "scraped"

    # Update competition metadata in session state with discussion insights
    current_metadata = tool_context.state.get(
        SESSION_KEYS["competition_metadata"], {}
    )
    if current_metadata:
        current_metadata["discussion_insights"] = result["posts"]
        tool_context.state[SESSION_KEYS["competition_metadata"]] = (
            current_metadata
        )

    return result


# Define the Scraper Agent
scraper_agent = LlmAgent(
    name="scraper_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Competition Research Agent for KaggleBot.

Your role is to research a Kaggle competition by scraping its page and
discussion posts, then provide a comprehensive summary of what you found.

When given a competition URL, you MUST:
1. Call `scrape_competition` with the URL to get competition metadata
2. Call `search_competition_discussions` with the URL to find tips/insights
3. Synthesize the results into a clear, structured summary

Your summary MUST include:
- Competition title and type (classification, regression, etc.)
- Evaluation metric (how submissions are scored)
- Dataset description (features, rows, target variable)
- Key insights from discussions (winning strategies, common pitfalls)
- Any important rules or constraints

Format your response as a well-organized report that the Data Agent
and Strategy Agent can use to make informed decisions.

Be concise but thorough. Focus on actionable information that would
help a data scientist plan their approach.""",
    tools=[_scrape_competition, _search_competition_discussions],
)
