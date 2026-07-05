"""
Trace Viewer — Visualizes traces as a timeline tree in the terminal.

Renders trace data as a hierarchical timeline showing agent execution
order, tool calls, timing, and status — similar to a flame graph
but in text format.

Concept demonstrated: Observability — Human-readable trace output
that makes debugging and demo presentations compelling.
"""

import json
from typing import Any

from observability.tracing import Tracer


def render_trace_tree(tracer: Tracer) -> str:
    """
    Renders a trace as a hierarchical tree with timing.

    Produces output like:
    ```
    [Trace: analyze-titanic-abc123]
    ├── Orchestrator (total: 45.2s)
    │   ├── Scraper Agent (8.1s) ✅
    │   │   ├── scrape_competition_page (3.2s) ✅
    │   │   └── search_discussions (4.9s) ✅
    │   ├── Data Agent (12.3s) ✅
    │   └── Strategy Agent (15.8s) ✅
    ```
    """
    lines = []
    trace_data = tracer.to_dict()
    spans = trace_data["spans"]

    # Header
    lines.append(
        f"[Trace: {trace_data['trace_name']}-{trace_data['trace_id']}]"
    )
    lines.append(
        f"  Total duration: {trace_data['total_duration_s']}s | "
        f"Spans: {trace_data['num_spans']}"
    )
    lines.append("")

    # Build parent-child relationships
    children: dict[str | None, list[dict]] = {}
    for span in spans:
        parent = span.get("parent_id")
        if parent not in children:
            children[parent] = []
        children[parent].append(span)

    # Render tree recursively
    root_spans = children.get(None, [])
    for i, span in enumerate(root_spans):
        is_last = i == len(root_spans) - 1
        _render_span(span, children, lines, "", is_last)

    return "\n".join(lines)


def _render_span(
    span: dict,
    children: dict[str | None, list[dict]],
    lines: list[str],
    prefix: str,
    is_last: bool,
) -> None:
    """Recursively renders a span and its children."""
    # Choose connector
    connector = "└── " if is_last else "├── "

    # Status icon
    status_icon = {
        "ok": "✅",
        "error": "❌",
        "running": "⏳",
    }.get(span["status"], "❓")

    # Type icon
    type_icon = {
        "agent": "🤖",
        "tool": "🔧",
        "llm": "🧠",
        "hitl": "⏸️",
        "generic": "📦",
    }.get(span["type"], "")

    # Format duration
    duration = span.get("duration_ms", 0)
    if duration > 1000:
        duration_str = f"{duration / 1000:.1f}s"
    else:
        duration_str = f"{duration:.0f}ms"

    # Build the line
    line = f"{prefix}{connector}{type_icon} {span['name']} ({duration_str}) {status_icon}"

    # Add key attributes
    attrs = span.get("attributes", {})
    if "tokens" in attrs:
        line += f" — {attrs['tokens']} tokens"
    if "error" in attrs:
        line += f" — {attrs['error'][:50]}"

    lines.append(line)

    # Render children
    child_spans = children.get(span["span_id"], [])
    child_prefix = prefix + ("    " if is_last else "│   ")
    for j, child in enumerate(child_spans):
        child_is_last = j == len(child_spans) - 1
        _render_span(child, children, lines, child_prefix, child_is_last)


def render_trace_summary(tracer: Tracer) -> str:
    """
    Renders a concise summary of the trace.

    Useful for quick overview in chat responses.
    """
    summary = tracer.get_summary()
    lines = [
        "═" * 50,
        "  📊 TRACE SUMMARY",
        "═" * 50,
        "",
        f"  Trace ID: {summary['trace_id']}",
        f"  Duration: {summary['total_duration_s']}s",
        f"  Agents: {summary['agent_count']}",
        f"  Tool calls: {summary['tool_count']}",
        f"  LLM calls: {summary['llm_count']}",
        f"  HITL pauses: {summary['hitl_count']}",
        "",
    ]

    if summary["agents"]:
        lines.append("  Agent Breakdown:")
        for agent in summary["agents"]:
            status_icon = "✅" if agent["status"] == "ok" else "❌"
            lines.append(
                f"    {status_icon} {agent['name']}: {agent['duration_s']}s"
            )
        lines.append("")

    if summary["slowest_span"]:
        lines.append(f"  Bottleneck: {summary['slowest_span']}")

    lines.append("═" * 50)
    return "\n".join(lines)


def export_trace_html(tracer: Tracer, filepath: str | None = None) -> str:
    """
    Exports the trace as a simple HTML timeline visualization.

    Args:
        tracer: The tracer to export
        filepath: Output filepath (default: output/traces/trace_<id>.html)

    Returns:
        Path to the generated HTML file.
    """
    import os

    from observability.tracing import TRACE_DIR

    if filepath is None:
        os.makedirs(TRACE_DIR, exist_ok=True)
        filepath = os.path.join(
            TRACE_DIR, f"trace_{tracer.trace_id}.html"
        )

    trace_data = tracer.to_dict()
    tree_text = render_trace_tree(tracer)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>KaggleBot Trace: {trace_data['trace_name']}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1e1e2e;
            color: #cdd6f4;
            padding: 2rem;
            max-width: 900px;
            margin: 0 auto;
        }}
        h1 {{ color: #89b4fa; }}
        .trace-tree {{
            background: #313244;
            padding: 1.5rem;
            border-radius: 8px;
            white-space: pre;
            line-height: 1.6;
            overflow-x: auto;
        }}
        .meta {{
            color: #a6adc8;
            margin-bottom: 1rem;
        }}
        .json-view {{
            background: #313244;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            max-height: 400px;
            overflow-y: auto;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <h1>🤖 KaggleBot Trace</h1>
    <div class="meta">
        Trace ID: {trace_data['trace_id']} |
        Duration: {trace_data['total_duration_s']}s |
        Spans: {trace_data['num_spans']}
    </div>
    <div class="trace-tree">{tree_text}</div>
    <h2>Raw Trace Data</h2>
    <div class="json-view">
        <pre>{json.dumps(trace_data, indent=2)}</pre>
    </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath


def load_and_display(filepath: str) -> str:
    """
    Loads a JSON trace file and renders it as a tree.

    Args:
        filepath: Path to the trace JSON file

    Returns:
        The rendered trace tree string.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reconstruct a tracer from the data
    tracer = Tracer(data.get("trace_name", "loaded"))
    tracer.trace_id = data.get("trace_id", "unknown")

    # We can't fully reconstruct spans, but we can render from the dict
    lines = []
    lines.append(f"[Trace: {data['trace_name']}-{data['trace_id']}]")
    lines.append(
        f"  Total duration: {data['total_duration_s']}s | "
        f"Spans: {data['num_spans']}"
    )
    lines.append("")

    # Build tree from raw data
    children: dict[str | None, list[dict]] = {}
    for span in data.get("spans", []):
        parent = span.get("parent_id")
        if parent not in children:
            children[parent] = []
        children[parent].append(span)

    root_spans = children.get(None, [])
    for i, span in enumerate(root_spans):
        is_last = i == len(root_spans) - 1
        _render_span(span, children, lines, "", is_last)

    return "\n".join(lines)
