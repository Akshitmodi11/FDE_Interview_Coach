"""MCP server "interview-guides": exposes the interview-technique guides in resources/.

Run it (stdio transport, which is what Claude Code uses):
    python mcp/server.py

Note: this folder deliberately has no __init__.py, so it never shadows the real
`mcp` package that fastmcp depends on.
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"

mcp = FastMCP("interview-guides")


@mcp.tool
def list_guides() -> list[str]:
    """List the available interview guides (names without the .md extension)."""
    return sorted(path.stem for path in RESOURCES_DIR.glob("*.md"))


@mcp.tool
def get_guide(name: str) -> str:
    """Return the full markdown of one guide, e.g. get_guide("decomposition-guide")."""
    stem = name.removesuffix(".md")
    available = list_guides()
    # Only names from list_guides() are allowed, which also blocks paths like "../.env".
    if stem not in available:
        raise ToolError(f"No guide named '{name}'. Available guides: {', '.join(available)}")
    return (RESOURCES_DIR / f"{stem}.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
