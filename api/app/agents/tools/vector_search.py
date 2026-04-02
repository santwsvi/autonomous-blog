"""Vector search tool for the Researcher agent."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding_service import search_similar

logger = structlog.get_logger()


async def vector_search(*, query: str, db: AsyncSession, limit: int = 5) -> str:
    """Search published posts for relevant context. Returns formatted text.

    Groups chunks by post — includes all relevant chunks per post,
    not just the first one.
    """
    try:
        results = await search_similar(query=query, db=db, limit=limit)

        if not results:
            logger.info("vector_search_no_results", query=query[:100])
            return ""

        # Group chunks by post, preserving order
        posts: dict[str, list[dict]] = {}
        for r in results:
            slug = r["slug"]
            if slug not in posts:
                posts[slug] = []
            posts[slug].append(r)

        context_parts = []
        for slug, chunks in posts.items():
            title = chunks[0]["title"]
            # Sort chunks by index for coherent reading order
            chunks.sort(key=lambda c: c["chunk_index"])
            text = "\n\n".join(c["chunk_text"] for c in chunks)
            context_parts.append(f"### From: {title} (/{slug})\n{text}")

        context = "\n\n---\n\n".join(context_parts)
        logger.info("vector_search_results", query=query[:100], chunks=len(results), unique_posts=len(posts))
        return context

    except Exception:
        logger.exception("vector_search_failed", query=query[:100])
        return ""  # Graceful degradation — researcher continues without RAG
