"""Publisher node — formats the final MDX and prepares for DB storage.

This is a deterministic node (no LLM calls). It sanitizes content,
builds frontmatter, and calculates metadata.
"""

import math
import re

import structlog

from app.agents.state import AgentState
from app.utils import generate_slug

logger = structlog.get_logger()

# Tags/elements NOT allowed in the sanitized MDX
BLOCKED_PATTERNS = [
    re.compile(r"<script[\s>].*?</script>", re.DOTALL | re.IGNORECASE),
    re.compile(r"<iframe[\s>].*?</iframe>", re.DOTALL | re.IGNORECASE),
    re.compile(r"<object[\s>].*?</object>", re.DOTALL | re.IGNORECASE),
    re.compile(r"<embed[\s>].*?</embed>", re.DOTALL | re.IGNORECASE),
    re.compile(r"on\w+\s*=\s*[\"'].*?[\"']", re.IGNORECASE),  # event handlers
    re.compile(r"javascript:", re.IGNORECASE),
]


async def publisher(state: AgentState) -> dict:
    logger.info("publisher_start")

    sanitized = _sanitize_mdx(state.draft)
    word_count = len(sanitized.split())
    reading_time = max(1, math.ceil(word_count / 200))

    slug = state.seo_slug or generate_slug(state.topic)

    logger.info(
        "publisher_done",
        slug=slug,
        word_count=word_count,
        reading_time=reading_time,
    )

    return {
        "final_mdx": sanitized,
        "word_count": word_count,
        "reading_time_minutes": reading_time,
    }


FRONTMATTER_PATTERN = re.compile(r"^---[\s\S]*?---\s*", re.MULTILINE)
MARKDOWN_WRAPPER = re.compile(r"^```(?:markdown|md|mdx)\s*\n([\s\S]*?)\n```\s*$")


def _sanitize_mdx(content: str) -> str:
    """Remove dangerous HTML/JS patterns, frontmatter, and LLM wrapper artifacts."""
    result = content.strip()
    match = MARKDOWN_WRAPPER.match(result)
    if match:
        result = match.group(1)
    result = FRONTMATTER_PATTERN.sub("", result)
    for pattern in BLOCKED_PATTERNS:
        result = pattern.sub("", result)
    return result.strip()
