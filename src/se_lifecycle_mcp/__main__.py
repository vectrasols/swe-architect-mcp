"""Command-line entry point for the SE Lifecycle MCP."""

from __future__ import annotations

import sys

from se_lifecycle_mcp.server import mcp


def main() -> None:
    """Start the MCP server."""
    transport = "stdio"
    if "--transport" in sys.argv:
        index = sys.argv.index("--transport")
        if index + 1 < len(sys.argv):
            transport = sys.argv[index + 1]
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
