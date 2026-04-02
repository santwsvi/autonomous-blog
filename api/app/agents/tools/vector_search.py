"""Vector search tool for the Researcher agent."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding_service import search_similar

logger = structlog.get_logger()


async def vector_search(*, query: str, db: AsyncSession, limit: int = 5) -> str:
    """Search published posts for relevant context. Returns formatted text."""
    try:
        results = await search_similar(query=query, db=db, limit=limit)

        if not results:
            logger.info("vector_search_no_results", query=query[:100])
            return ""

        context_parts = []
        seen_posts = set()
        for r in results:
            if r["slug"] not in seen_posts:
                context_parts.append(f"### From: {r['title']} (/{r['slug']})\n{r['chunk_text']}")
                seen_posts.add(r["slug"])

        context = "\n\n---\n\n".join(context_parts)
        logger.info("vector_search_results", query=query[:100], results=len(results), unique_posts=len(seen_posts))
        return context

    except Exception:
        logger.exception("vector_search_failed", query=query[:100])
        return ""  # Graceful degradation — researcher continues without RAG
