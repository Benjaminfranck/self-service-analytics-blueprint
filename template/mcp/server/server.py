"""MCP server (stdio) exposing the governed analytics layer.

The agent talks to THIS server over MCP and sends structured metric requests — never SQL, never
credentials. The server holds the (read-only) DB connection and compiles + runs the SQL. Note that
`compile_metric` has NO `tenant` parameter: the tenant is bound server-side (from DEMO_TENANT /
session), so the agent cannot widen scope. This is a thin wrapper over engine.py.

Run:  WAREHOUSE_DSN=... python server.py
"""
from __future__ import annotations
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import engine

mcp = FastMCP("self-serve-analytics")

_REFERENCE_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "reference"


@mcp.tool()
def list_metrics() -> list[dict]:
    """Return the governed metric catalog (names, kind, owner, tier, dimensions). Metadata only."""
    return engine.list_metrics()


@mcp.tool()
def compile_metric(metric: str, dimensions: list[str] | None = None,
                   filters: list[str] | None = None, grain: str | None = None,
                   order_by: str | None = None, limit: int | None = None) -> dict:
    """Compile {metric, dimensions, filters, grain} to SQL, run it READ-ONLY, and return
    rows + the generated SQL (as provenance) + freshness. Tenant is injected server-side.
    Unknown objects fail closed with an error + suggestions (never a guess)."""
    try:
        return engine.compile_metric(metric, dimensions=dimensions, filters=filters,
                                     grain=grain, order_by=order_by, limit=limit)
    except engine.MetricError as e:
        return e.to_dict()


@mcp.tool()
def resolve_entity(terms: list[str]) -> dict:
    """Map question nouns to governed entities + join paths (metadata)."""
    return engine.resolve_entity(terms)


@mcp.tool()
def get_reference_doc(domain: str) -> str:
    """Return the LLM-facing reference doc for a domain (e.g. 'findings', 'assets', 'risk')."""
    path = _REFERENCE_DIR / f"{domain}.md"
    if not path.exists():
        return f"No reference doc for '{domain}'. Available: " + ", ".join(
            p.stem for p in sorted(_REFERENCE_DIR.glob("*.md")))
    return path.read_text()


@mcp.tool()
def source_freshness(source: str | None = None) -> dict:
    """Max ingested_at + row count for the tenant's findings (for the provenance footer)."""
    return engine.source_freshness()


if __name__ == "__main__":
    mcp.run()
