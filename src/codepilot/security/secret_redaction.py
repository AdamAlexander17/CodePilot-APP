"""Detects and masks likely secrets before file contents leave the process."""

import re

BLOCKED_FILENAME_PATTERNS = (
    re.compile(r"^\.env(\..+)?$"),
    re.compile(r".*\.pem$"),
    re.compile(r".*\.key$"),
)

# Rough patterns for common secret shapes. Not exhaustive - a first line of defense, not a guarantee.
SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[\w\-\.]{8,}['\"]?"),
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key id shape
)

REDACTED = "***REDACTED***"


def is_blocked_filename(filename: str) -> bool:
    return any(pattern.match(filename) for pattern in BLOCKED_FILENAME_PATTERNS)


def redact_secrets(content: str) -> str:
    redacted = content
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(REDACTED, redacted)
    return redacted
