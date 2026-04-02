"""Writer node — generates or revises the blog post draft."""

import hashlib
from pathlib import Path

import structlog

from app.agents.state import AgentState
from app.agents.utils import merge_usage
from app.services.llm_service import complete

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "writer.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()
PROMPT_HASH = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()[:16]


async def writer(state: AgentState) -> dict:
    iteration = state.iteration + 1
    is_revision = bool(state.feedback)
    logger.info("writer_start", iteration=iteration, is_revision=is_revision)

    user_content = (
        f"## Topic\n{state.topic}\n\n"
        f"## Author Instructions\n{state.instructions or 'None'}\n\n"
        f"## Language\n{state.language}\n\n"
        f"## Research Context\n{state.research_context}\n\n"
    )

    if is_revision:
        user_content += (
            f"## Previous Draft\n{state.draft}\n\n"
            f"## Editor Feedback (MUST address)\n{state.feedback}\n\n"
            "Rewrite the article addressing ALL the feedback above. "
            "Keep what was good, fix what was flagged."
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    content, usage = await complete(messages=messages, model="gpt-4o-mini", max_tokens=4000, temperature=0.7)

    logger.info("writer_done", iteration=iteration, draft_length=len(content))

    prompt_versions = dict(state.prompt_versions or {})
    prompt_versions["writer"] = PROMPT_HASH

    return {
        "draft": content,
        "iteration": iteration,
        "model_usage": merge_usage(state.model_usage, f"writer_v{iteration}", usage),
        "prompt_versions": prompt_versions,
    }
