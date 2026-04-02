"""Editor node — reviews draft, scores quality, approves or requests revision."""

import hashlib
import re
from pathlib import Path

import structlog

from app.agents.state import AgentState, QualityScores
from app.agents.utils import merge_usage
from app.services.llm_service import complete

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "editor.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()
PROMPT_HASH = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()[:16]


async def editor(state: AgentState) -> dict:
    logger.info("editor_start", iteration=state.iteration)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"## Original Topic\n{state.topic}\n\n"
                f"## Author Instructions\n{state.instructions or 'None'}\n\n"
                f"## Draft to Review\n{state.draft}"
            ),
        },
    ]

    content, usage = await complete(messages=messages, model="gpt-4o", max_tokens=2000, temperature=0.3)

    scores = _parse_scores(content)
    approved = _parse_approved(content)
    feedback = _parse_feedback(content)

    logger.info(
        "editor_done",
        overall_score=scores.overall,
        approved=approved,
        iteration=state.iteration,
    )

    prompt_versions = dict(state.prompt_versions or {})
    prompt_versions["editor"] = PROMPT_HASH

    return {
        "quality_scores": scores,
        "approved": approved,
        "feedback": feedback if not approved else "",
        "model_usage": merge_usage(state.model_usage, f"editor_v{state.iteration}", usage),
        "prompt_versions": prompt_versions,
    }


def _parse_scores(content: str) -> QualityScores:
    """Parse quality scores from editor output."""
    defaults = QualityScores()
    try:
        for field in ["readability", "coherence", "depth", "originality", "factual_accuracy", "overall"]:
            match = re.search(rf"{field}:\s*([\d.]+)", content, re.IGNORECASE)
            if match:
                setattr(defaults, field, min(1.0, max(0.0, float(match.group(1)))))
    except (ValueError, AttributeError):
        pass
    return defaults


def _parse_approved(content: str) -> bool:
    match = re.search(r"APPROVED:\s*(true|false)", content, re.IGNORECASE)
    if match:
        return match.group(1).lower() == "true"
    return False


def _parse_feedback(content: str) -> str:
    match = re.search(r"FEEDBACK:\s*(.+)", content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return content
