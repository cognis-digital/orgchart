"""ORGCHART MCP server — exposes scan() as an MCP tool for Cognis.Studio."""
from __future__ import annotations
from orgchart.core import scan, to_json

def serve() -> int:
    """Start an MCP stdio server. Requires the optional 'mcp' extra:
        pip install "cognis-orgchart[mcp]"
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        print("Install the MCP extra: pip install 'cognis-orgchart[mcp]'")
        return 1
    app = FastMCP("orgchart")

    @app.tool()
    def orgchart_scan(target: str) -> str:
        """Org charts and headcount plans generated from CSV / HRIS export. Returns JSON findings."""
        return to_json(scan(target))

    app.run()
    return 0
