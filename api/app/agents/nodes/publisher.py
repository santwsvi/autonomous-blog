"""Publisher node — formats the final MDX and prepares for DB storage.

This is a deterministic node (no LLM calls). It sanitizes content,
builds frontmatter, and calculates metadata.
"""

import math
import re

import structlog

from app.agents.state import AgentState

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

    slug = state.seo_slug or _generate_slug(state.topic)
    # Ensure slug uniqueness will be handled by the API layer

    logger.info(
        "publisher_done",
        slug=slug,
        word_count=word_count,
        reading_time=reading_time,
    )

    return {
        "final_mdx": sanitized,
    }


FRONTMATTER_PATTERN = re.compile(r"^---[\s\S]*?---\s*", re.MULTILINE)
MARKDOWN_WRAPPER = re.compile(r"^```(?:markdown|md|mdx)\s*\n([\s\S]*?)\n```\s*$")


def _sanitize_mdx(content: str) -> str:
    """Remove dangerous HTML/JS patterns, frontmatter, and LLM wrapper artifacts."""
    result = content.strip()
    # Strip ```markdown ... ``` wrapper that LLMs sometimes add
    match = MARKDOWN_WRAPPER.match(result)
    if match:
        result = match.group(1)
    # Strip frontmatter
    result = FRONTMATTER_PATTERN.sub("", result)
    # Strip dangerous patterns
    for pattern in BLOCKED_PATTERNS:
        result = pattern.sub("", result)
    return result.strip()


def _generate_slug(topic: str) -> str:
    """Generate a URL-friendly slug from the topic."""
    slug = topic.lower().strip()
    slug = re.sub(r"[àáâãäå]", "a", slug)
    slug = re.sub(r"[èéêë]", "e", slug)
    slug = re.sub(r"[ìíîï]", "i", slug)
    slug = re.sub(r"[òóôõö]", "o", slug)
    slug = re.sub(r"[ùúûü]", "u", slug)
    slug = re.sub(r"[ç]", "c", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:80]
