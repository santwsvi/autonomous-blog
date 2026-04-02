"""SEO Optimizer node — generates metadata for the post."""

import json
import re

import structlog

from app.agents.state import AgentState
from app.agents.utils import merge_usage
from app.services.llm_service import complete

logger = structlog.get_logger()

SEO_SYSTEM = """You are an SEO specialist for a technical blog. Generate metadata for the given blog post.

## Output Format (STRICT JSON)

```json
{
  "title": "SEO-optimized title (max 60 chars)",
  "description": "Meta description (max 155 chars)",
  "slug": "url-friendly-slug",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}
```

## Rules
- Title should be compelling and include primary keyword
- Description should summarize the value proposition
- Slug must be lowercase, hyphen-separated, no special chars
- Tags: 3-7 relevant tags, lowercase
- Respond ONLY with the JSON block, nothing else
"""


async def seo_optimizer(state: AgentState) -> dict:
    logger.info("seo_optimizer_start")

    # Send more context for better SEO (1500 chars instead of 500)
    messages = [
        {"role": "system", "content": SEO_SYSTEM},
        {
            "role": "user",
            "content": (
                f"## Blog Post Title Area\n{state.topic}\n\n"
                f"## Post Content (summary)\n{state.draft[:1500]}\n\n"
                f"## Language\n{state.language}"
            ),
        },
    ]

    content, usage = await complete(messages=messages, model="gpt-4o-mini", max_tokens=500, temperature=0.3)

    seo = _parse_seo_json(content)

    logger.info("seo_optimizer_done", slug=seo.get("slug", ""))

    return {
        "seo_title": seo.get("title", state.topic),
        "seo_description": seo.get("description", ""),
        "seo_slug": seo.get("slug", ""),
        "seo_tags": seo.get("tags", []),
        "model_usage": merge_usage(state.model_usage, "seo_optimizer", usage),
    }


def _parse_seo_json(content: str) -> dict:
    """Extract JSON from the LLM response."""
    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(content)
    except (json.JSONDecodeError, AttributeError):
        logger.warning("seo_json_parse_failed", content=content[:200])
        return {}
