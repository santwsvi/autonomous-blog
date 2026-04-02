"""Researcher node — gathers context from existing posts (RAG) and LLM knowledge."""

import hashlib
from pathlib import Path

import structlog

from app.agents.state import AgentState
from app.agents.utils import merge_usage
from app.services.llm_service import complete

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "researcher.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()
PROMPT_HASH = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()[:16]


async def researcher(state: AgentState) -> dict:
    logger.info("researcher_start", topic=state.topic)

    # RAG context is injected by the generation service before the graph runs
    rag_section = ""
    if state.rag_context:
        rag_section = f"\n\n## Existing Blog Posts (for context and consistency)\n{state.rag_context}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"## Topic\n{state.topic}\n\n"
                f"## Author Instructions\n{state.instructions or 'None'}\n\n"
                f"## Language\n{state.language}"
                f"{rag_section}"
            ),
        },
    ]

    content, usage = await complete(messages=messages, model="gpt-4o-mini", max_tokens=3000, temperature=0.5)

    logger.info("researcher_done", context_length=len(content), has_rag=bool(state.rag_context))

    prompt_versions = dict(state.prompt_versions or {})
    prompt_versions["researcher"] = PROMPT_HASH

    return {
        "research_context": content,
        "model_usage": merge_usage(state.model_usage, "researcher", usage),
        "prompt_versions": prompt_versions,
    }
