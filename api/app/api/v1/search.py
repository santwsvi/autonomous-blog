"""Search API — semantic search across published posts."""

import structlog
from fastapi import APIRouter, Query

from app.api.deps import Db
from app.services.embedding_service import search_similar

logger = structlog.get_logger()
router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search_posts(
    db: Db,
    q: str = Query(..., min_length=2, max_length=500, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
) -> dict:
    """Semantic search across published posts."""
    results = await search_similar(query=q, db=db, limit=limit)

    return {
        "query": q,
        "results": [
            {
                "title": r["title"],
                "slug": r["slug"],
                "excerpt": r["chunk_text"][:200],
                "similarity": r["similarity"],
            }
            for r in results
        ],
        "total": len(results),
    }
