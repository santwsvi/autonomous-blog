"""Related posts API — find semantically similar posts."""

import structlog
from fastapi import APIRouter, HTTPException, Query

from app.api.deps import Db
from app.services.embedding_service import search_similar

logger = structlog.get_logger()
router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/{slug}/related")
async def get_related_posts(
    slug: str,
    db: Db,
    limit: int = Query(3, ge=1, le=10),
) -> dict:
    """Find posts semantically related to the given post."""
    from sqlalchemy import text

    # Get post_id from slug
    result = await db.execute(text("SELECT id FROM posts WHERE slug = :slug"), {"slug": slug})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")

    post_id = row[0]

    # Get post title for the search query
    title_result = await db.execute(text("SELECT title, excerpt FROM posts WHERE id = :id"), {"id": post_id})
    title_row = title_result.fetchone()
    query = f"{title_row[0]} {title_row[1] or ''}" if title_row else slug

    results = await search_similar(query=query, db=db, limit=limit, exclude_post_id=post_id)

    # Deduplicate by slug
    seen = set()
    unique = []
    for r in results:
        if r["slug"] not in seen:
            seen.add(r["slug"])
            unique.append(
                {
                    "title": r["title"],
                    "slug": r["slug"],
                    "excerpt": r["chunk_text"][:150],
                    "similarity": r["similarity"],
                }
            )

    return {"related": unique}
