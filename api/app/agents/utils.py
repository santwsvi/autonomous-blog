"""Shared utilities for agent nodes."""


def merge_usage(existing: dict, step: str, usage: dict) -> dict:
    """Merge a new usage entry into the existing usage dict."""
    result = dict(existing)
    result[step] = usage
    return result
