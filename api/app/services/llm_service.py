"""LLM service — thin wrapper over OpenAI SDK with usage tracking.

Can be extended to support Anthropic/Groq by adding provider-specific methods.
"""

import httpx
import structlog
from openai import AsyncOpenAI

from app.config import settings

logger = structlog.get_logger()

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        http_client = None
        if not settings.llm_ssl_verify:
            http_client = httpx.AsyncClient(verify=False)
        _client = AsyncOpenAI(api_key=settings.openai_api_key, http_client=http_client)
    return _client


async def complete(
    *,
    messages: list[dict],
    model: str = "gpt-4o-mini",
    max_tokens: int = 4000,
    temperature: float = 0.7,
) -> tuple[str, dict]:
    """Call OpenAI chat completion and return (content, usage_dict)."""
    client = get_openai_client()

    logger.debug("llm_call", model=model, message_count=len(messages), max_tokens=max_tokens)

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    content = response.choices[0].message.content or ""
    usage = {
        "model": model,
        "input_tokens": response.usage.prompt_tokens if response.usage else 0,
        "output_tokens": response.usage.completion_tokens if response.usage else 0,
    }

    logger.info(
        "llm_response",
        model=model,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        content_length=len(content),
    )

    return content, usage
