"""Metrics API — aggregated stats for the admin dashboard."""

import structlog
from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import Auth, Db

logger = structlog.get_logger()
router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
async def get_metrics(db: Db, _user: Auth) -> dict:
    """Aggregated blog metrics (authenticated — admin only)."""

    # Posts by status
    posts_result = await db.execute(text("SELECT status, count(*) FROM posts GROUP BY status"))
    posts_by_status = {row[0]: row[1] for row in posts_result.fetchall()}

    # Generation stats
    gen_result = await db.execute(
        text("""
            SELECT
                count(*) AS total,
                count(*) FILTER (WHERE status = 'completed') AS completed,
                count(*) FILTER (WHERE status = 'failed') AS failed,
                avg(duration_seconds) FILTER (WHERE status = 'completed') AS avg_duration,
                avg((quality_scores->>'overall')::float) FILTER (WHERE quality_scores IS NOT NULL) AS avg_quality
            FROM generation_jobs
        """)
    )
    gen_row = gen_result.fetchone()

    # LLM cost estimate (rough: $0.15/1M input, $0.60/1M output for gpt-4o-mini; $2.50/$10 for gpt-4o)
    cost_result = await db.execute(
        text("""
            SELECT
                sum(
                    CASE
                        WHEN value->>'model' LIKE '%4o-mini%' THEN
                            (value->>'input_tokens')::float * 0.00000015 +
                            (value->>'output_tokens')::float * 0.0000006
                        ELSE
                            (value->>'input_tokens')::float * 0.0000025 +
                            (value->>'output_tokens')::float * 0.00001
                    END
                ) AS total_cost
            FROM generation_jobs, jsonb_each(model_usage) AS kv(key, value)
            WHERE model_usage IS NOT NULL
        """)
    )
    total_cost = cost_result.scalar() or 0

    # Embeddings
    embed_result = await db.execute(text("SELECT count(*) FROM embeddings WHERE embedding IS NOT NULL"))
    total_embeddings = embed_result.scalar() or 0

    # Recent generations
    recent_result = await db.execute(
        text("""
            SELECT g.id, g.prompt, g.status, g.quality_scores->>'overall' as score,
                   g.duration_seconds, g.iterations, g.created_at,
                   p.title, p.slug
            FROM generation_jobs g
            LEFT JOIN posts p ON p.id = g.post_id
            ORDER BY g.created_at DESC
            LIMIT 5
        """)
    )
    recent = [
        {
            "id": str(row[0]),
            "prompt": row[1][:100],
            "status": row[2],
            "quality_score": float(row[3]) if row[3] else None,
            "duration_seconds": row[4],
            "iterations": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "post_title": row[7],
            "post_slug": row[8],
        }
        for row in recent_result.fetchall()
    ]

    return {
        "posts": {
            "total": sum(posts_by_status.values()),
            "by_status": posts_by_status,
        },
        "generations": {
            "total": gen_row[0] if gen_row else 0,
            "completed": gen_row[1] if gen_row else 0,
            "failed": gen_row[2] if gen_row else 0,
            "avg_duration_seconds": round(float(gen_row[3]), 1) if gen_row and gen_row[3] else None,
            "avg_quality_score": round(float(gen_row[4]), 3) if gen_row and gen_row[4] else None,
        },
        "llm": {
            "total_cost_usd": round(float(total_cost), 4),
        },
        "embeddings": {
            "total_chunks": total_embeddings,
        },
        "recent_generations": recent,
    }
