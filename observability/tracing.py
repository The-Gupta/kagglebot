"""
Tracing — OpenTelemetry integration for full pipeline observability.

Captures structured traces across all agent and tool calls, providing
visibility into execution timing, token usage, and data flow.

Concept demonstrated: Observability — Production-grade tracing
that shows the full agent pipeline with timing and details.
"""

import json
import os
import time
import uuid
from contextlib import contextmanager
from typing import Any, Generator


# Default trace output directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACE_DIR = os.path.join(_PROJECT_ROOT, "output", "traces")


class Span:
    """Represents a single unit of work in a trace."""

    def __init__(
        self,
        name: str,
        span_type: str = "generic",
        parent_id: str | None = None,
        trace_id: str | None = None,
    ):
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id or str(uuid.uuid4())[:12]
        self.parent_id = parent_id
        self.name = name
        self.span_type = span_type  # agent, tool, llm, hitl
        self.start_time = time.time()
        self.end_time: float | None = None
        self.status = "running"
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []

    def set_attribute(self, key: str, value: Any) -> None:
        """Sets a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Records an event within this span."""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })

    def end(self, status: str = "ok") -> None:
        """Marks the span as complete."""
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        end = self.end_time or time.time()
        return round((end - self.start_time) * 1000, 1)

    @property
    def duration_s(self) -> float:
        """Duration in seconds."""
        return round(self.duration_ms / 1000, 2)

    def to_dict(self) -> dict[str, Any]:
        """Serializes the span to a dictionary."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "type": self.span_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


class Tracer:
    """
    Collects and manages traces for a KaggleBot pipeline run.

    Provides context managers for creating spans, and exports
    traces to JSON for visualization.
    """

    def __init__(self, trace_name: str = "kagglebot-run"):
        self.trace_id = str(uuid.uuid4())[:12]
        self.trace_name = trace_name
        self.spans: list[Span] = []
        self._current_span: Span | None = None
        self.start_time = time.time()

    @contextmanager
    def span(
        self,
        name: str,
        span_type: str = "generic",
    ) -> Generator[Span, None, None]:
        """
        Context manager that creates and manages a trace span.

        Usage:
            with tracer.span("scraper_agent", "agent") as s:
                s.set_attribute("url", competition_url)
                # ... do work ...
                s.add_event("scraped_page", {"status": 200})
        """
        parent_id = self._current_span.span_id if self._current_span else None
        s = Span(
            name=name,
            span_type=span_type,
            parent_id=parent_id,
            trace_id=self.trace_id,
        )
        self.spans.append(s)

        previous_span = self._current_span
        self._current_span = s

        try:
            yield s
            s.end("ok")
        except Exception as e:
            s.set_attribute("error", str(e))
            s.end("error")
            raise
        finally:
            self._current_span = previous_span

    def create_span(self, name: str, span_type: str = "generic") -> Span:
        """Creates a span manually (for non-context-manager use)."""
        parent_id = self._current_span.span_id if self._current_span else None
        s = Span(
            name=name,
            span_type=span_type,
            parent_id=parent_id,
            trace_id=self.trace_id,
        )
        self.spans.append(s)
        return s

    def get_total_duration_s(self) -> float:
        """Returns total trace duration in seconds."""
        return round(time.time() - self.start_time, 2)

    def to_dict(self) -> dict[str, Any]:
        """Serializes the full trace."""
        return {
            "trace_id": self.trace_id,
            "trace_name": self.trace_name,
            "start_time": self.start_time,
            "total_duration_s": self.get_total_duration_s(),
            "num_spans": len(self.spans),
            "spans": [s.to_dict() for s in self.spans],
        }

    def export_json(self, filepath: str | None = None) -> str:
        """Exports the trace as a JSON file."""
        if filepath is None:
            os.makedirs(TRACE_DIR, exist_ok=True)
            filepath = os.path.join(
                TRACE_DIR, f"trace_{self.trace_id}.json"
            )

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    def get_summary(self) -> dict[str, Any]:
        """Returns a summary of the trace."""
        agent_spans = [s for s in self.spans if s.span_type == "agent"]
        tool_spans = [s for s in self.spans if s.span_type == "tool"]
        llm_spans = [s for s in self.spans if s.span_type == "llm"]
        hitl_spans = [s for s in self.spans if s.span_type == "hitl"]

        return {
            "trace_id": self.trace_id,
            "total_duration_s": self.get_total_duration_s(),
            "agent_count": len(agent_spans),
            "tool_count": len(tool_spans),
            "llm_count": len(llm_spans),
            "hitl_count": len(hitl_spans),
            "agents": [
                {"name": s.name, "duration_s": s.duration_s, "status": s.status}
                for s in agent_spans
            ],
            "slowest_span": max(
                self.spans, key=lambda s: s.duration_ms
            ).name if self.spans else None,
        }


# Singleton tracer for the current run
_current_tracer: Tracer | None = None


def get_tracer(trace_name: str = "kagglebot-run") -> Tracer:
    """Returns the current tracer or creates a new one."""
    global _current_tracer
    if _current_tracer is None:
        _current_tracer = Tracer(trace_name)
    return _current_tracer


def reset_tracer() -> None:
    """Resets the current tracer (for new runs)."""
    global _current_tracer
    _current_tracer = None
