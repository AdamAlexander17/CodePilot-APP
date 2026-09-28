"""Git MCP server: exposes read-only tools over a target repository."""

import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

REPO_ROOT = Path(os.environ["GIT_MCP_REPO_PATH"]).resolve()

mcp = MCPServer("git-server")


@mcp.tool()
def list_files() -> list[str]:
    """List every file in the repository, relative to its root."""
    files = []
    for file_path in REPO_ROOT.rglob("*"):
        if file_path.is_file() and ".git" not in file_path.parts:
            files.append(str(file_path.relative_to(REPO_ROOT)))
    return sorted(files)


if __name__ == "__main__":
    mcp.run()
