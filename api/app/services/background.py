"""Background task helper — fire-and-forget coroutines with GC protection."""

import asyncio
from collections.abc import Coroutine
from typing import Any

_tasks: set[asyncio.Task] = set()


def schedule(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    """Schedule a coroutine as a background task. Prevents GC collection."""
    task = asyncio.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return task
