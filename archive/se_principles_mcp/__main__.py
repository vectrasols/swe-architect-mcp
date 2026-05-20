"""
Entry point for running the SE Principles MCP Server.

Usage:
    python -m se_principles_mcp              # stdio transport (default)
    python -m se_principles_mcp --transport streamable-http  # HTTP transport
"""

import sys

from se_principles_mcp.server import mcp


def main() -> None:
    """Start the SE Principles MCP Server."""
    transport = "stdio"

    # Simple arg parsing for transport override
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
