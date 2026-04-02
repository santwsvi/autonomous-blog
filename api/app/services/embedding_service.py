"""Embedding service — generate and store embeddings for blog posts."""

import uuid

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import get_openai_client

logger = structlog.get_logger()

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_MAX_CHARS = 2000
CHUNK_OVERLAP_CHARS = 400


async def embed_text(content: str) -> list[float]:
    """Generate embedding vector for a text string."""
    if not content or not content.strip():
        raise ValueError("Cannot embed empty content")

    client = get_openai_client()
    response = await client.embeddings.create(model=EMBEDDING_MODEL, input=content.strip())
    return response.data[0].embedding


async def embed_post(*, post_id: uuid.UUID, content: str, db: AsyncSession) -> int:
    """Chunk a post's content, generate embeddings, and store in DB.

    Returns the number of chunks created.
    """
    if not content or not content.strip():
        logger.warning("embed_post_empty_content", post_id=str(post_id))
        return 0

    # Remove existing embeddings for this post
    await db.execute(text("DELETE FROM embeddings WHERE post_id = :pid"), {"pid": post_id})

    chunks = chunk_text(content)
    if not chunks:
        logger.warning("embed_post_no_chunks", post_id=str(post_id))
        return 0

    count = 0
    for i, chunk in enumerate(chunks):
        try:
            vector = await embed_text(chunk)
            vector_str = "[" + ",".join(str(v) for v in vector) + "]"

            await db.execute(
                text("""
                    INSERT INTO embeddings (id, post_id, chunk_index, chunk_text, vector_id, token_count, embedding)
                    VALUES (gen_random_uuid(), :post_id, :chunk_index, :chunk_text, :vector_id, :token_count, cast(:embedding AS vector))
                """),
                {
                    "post_id": post_id,
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "vector_id": f"{post_id}_{i}",
                    "token_count": len(chunk.split()),
                    "embedding": vector_str,
                },
            )
            count += 1
        except Exception:
            logger.exception("embed_chunk_failed", post_id=str(post_id), chunk_index=i)

    logger.info("embed_post_done", post_id=str(post_id), chunks=count)
    return count


async def search_similar(
    *, query: str, db: AsyncSession, limit: int = 5, exclude_post_id: uuid.UUID | None = None
) -> list[dict]:
    """Search for similar content using cosine similarity (exact scan, no index)."""
    if not query or not query.strip():
        return []

    query_vector = await embed_text(query)
    vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"

    exclude_clause = "AND e.post_id != :exclude_id" if exclude_post_id else ""
    params: dict = {"query_vec": vector_str, "lim": limit}
    if exclude_post_id:
        params["exclude_id"] = exclude_post_id

    result = await db.execute(
        text(f"""
            SELECT e.post_id, e.chunk_text, e.chunk_index,
                   p.title, p.slug,
                   1 - (e.embedding <=> cast(:query_vec AS vector)) AS similarity
            FROM embeddings e
            JOIN posts p ON p.id = e.post_id
            WHERE e.embedding IS NOT NULL
              AND p.status = 'published'
              {exclude_clause}
            ORDER BY e.embedding <=> cast(:query_vec AS vector)
            LIMIT :lim
        """),
        params,
    )

    rows = result.fetchall()
    return [
        {
            "post_id": str(row.post_id),
            "chunk_text": row.chunk_text,
            "chunk_index": row.chunk_index,
            "title": row.title,
            "slug": row.slug,
            "similarity": round(float(row.similarity), 4),
        }
        for row in rows
    ]


def chunk_text(content: str, chunk_size: int = CHUNK_MAX_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    """Split text into overlapping chunks by character count."""
    content = content.strip()
    if not content:
        return []

    if len(content) <= chunk_size:
        return [content]

    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunk = content[start:end]

        # Try to break at paragraph or sentence boundary
        if end < len(content):
            for sep in ["\n\n", "\n", ". ", " "]:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size * 0.5:
                    chunk = chunk[: last_sep + len(sep)]
                    end = start + len(chunk)
                    break

        chunks.append(chunk.strip())
        start = end - overlap

    return [c for c in chunks if c]
