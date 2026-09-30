"""Git MCP server: exposes read-only tools over a target repository."""
from codepilot.security.secret_redaction import is_blocked_filename, redact_secrets

import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

REPO_ROOT = Path(os.environ["GIT_MCP_REPO_PATH"]).resolve()

mcp = MCPServer("git-server")


IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache", ".mypy_cache"}


@mcp.tool()
def list_files() -> list[str]:
    """List every file in the repository, relative to its root, skipping noise directories."""
    files = []
    for file_path in REPO_ROOT.rglob("*"):
        if file_path.is_file() and not IGNORED_DIRS.intersection(file_path.parts):
            files.append(str(file_path.relative_to(REPO_ROOT)))
    return sorted(files)

@mcp.tool()
def read_file(path: str) -> str:
    """Read one file's contents, relative to the repo root. Blocks secret files and redacts likely secrets."""
    if is_blocked_filename(Path(path).name):
        return f"Error: reading '{path}' is blocked (looks like a credentials file)."

    target = (REPO_ROOT / path).resolve()
    if not target.is_relative_to(REPO_ROOT):
        return f"Error: '{path}' is outside the repository."
    if not target.is_file():
        return f"Error: '{path}' is not a file."

    content = target.read_text(encoding="utf-8", errors="replace")
    return redact_secrets(content)


if __name__ == "__main__":
    mcp.run()
