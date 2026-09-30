"""Git MCP server: exposes read-only tools over a target repository."""
from codepilot.security.secret_redaction import is_blocked_filename, redact_secrets
import subprocess

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


@mcp.tool()
def get_commit_log(limit: int = 20) -> list[dict[str, str]]:
    """Get the most recent commits, newest first."""
    separator = "\x1f"  # unit separator, unlikely to appear in commit messages
    result = subprocess.run(
        [
            "git", "log", f"-{limit}",
            f"--pretty=format:%H{separator}%an{separator}%ad{separator}%s",
            "--date=iso",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    commits = []
    for line in result.stdout.splitlines():
        commit_hash, author, date, message = line.split(separator)
        commits.append({
            "hash": commit_hash,
            "author": author,
            "date": date,
            "message": message,
        })
    return commits


@mcp.tool()
def get_file_history(path: str) -> list[dict[str, str]]:
    """Get the commits that touched a specific file, newest first."""
    target = (REPO_ROOT / path).resolve()
    if not target.is_relative_to(REPO_ROOT):
        return [{"error": f"'{path}' is outside the repository."}]

    separator = "\x1f"
    result = subprocess.run(
        [
            "git", "log",
            f"--pretty=format:%H{separator}%an{separator}%ad{separator}%s",
            "--date=iso",
            "--", path,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    if not result.stdout.strip():
        return []

    commits = []
    for line in result.stdout.splitlines():
        commit_hash, author, date, message = line.split(separator)
        commits.append({
            "hash": commit_hash,
            "author": author,
            "date": date,
            "message": message,
        })
    return commits


@mcp.tool()
def search_code(query: str, max_results: int = 50) -> list[dict[str, str]]:
    """Search file contents for a string, like grep. Returns matching lines with file and line number."""
    result = subprocess.run(
        ["git", "grep", "-n", "-I", "--fixed-strings", query],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode not in (0, 1):  # 1 = "no matches", not an error
        return [{"error": result.stderr.strip()}]

    matches = []
    for line in result.stdout.splitlines()[:max_results]:
        file_path, line_number, text = line.split(":", 2)
        matches.append({"file": file_path, "line": line_number, "text": text.strip()})
    return matches


if __name__ == "__main__":
    mcp.run()
