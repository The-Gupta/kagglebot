"""
KaggleBot — Custom Server with Chat UI + ADK API

Wraps the ADK web server to add a chat UI at the root path.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.routing import Route


def create_app():
    """Create the combined ADK + Chat UI app."""
    from google.adk.cli.fast_api import get_fast_api_app

    agents_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(agents_dir, "static")

    app = get_fast_api_app(
        agents_dir=agents_dir,
        web=True,
    )

    # Read the chat UI HTML at startup
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r") as f:
        chat_html = f.read()

    # Replace ADK's root route with our chat UI
    # Find and remove existing root routes
    new_routes = []
    for route in app.routes:
        if isinstance(route, Route) and route.path == "/":
            continue  # Skip the ADK root redirect
        new_routes.append(route)
    app.routes[:] = new_routes

    # Add our chat UI at root
    @app.get("/", response_class=HTMLResponse)
    async def serve_chat_ui():
        return HTMLResponse(content=chat_html)

    return app


app = create_app()
