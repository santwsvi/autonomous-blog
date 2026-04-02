"""Structlog processor that redacts sensitive values from log entries."""

import re

REDACT_PATTERNS = [
    re.compile(r"(Bearer\s+)\S+", re.IGNORECASE),
    re.compile(r"(sk-)\S+"),
    re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)\S+", re.IGNORECASE),
    re.compile(r"(\$2[aby]\$\d+\$)\S+"),  # bcrypt hashes
]

REDACT_KEYS = {"password", "secret", "token", "api_key", "authorization"}


def redact_sensitive(_logger, _method, event_dict: dict) -> dict:
    """Redact sensitive values from structured log entries."""
    for key, value in list(event_dict.items()):
        if not isinstance(value, str):
            continue
        if key.lower() in REDACT_KEYS:
            event_dict[key] = "[REDACTED]"
            continue
        for pattern in REDACT_PATTERNS:
            value = pattern.sub(r"\1[REDACTED]", value)
        event_dict[key] = value
    return event_dict
