"""Generation service — orchestrates article generation and persistence."""

import time
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import generation_graph
from app.agents.state import AgentState
from app.models.post import GenerationJob, JobStatus, PostStatus
from app.repositories.post_repository import PostRepository
from app.utils import generate_slug

logger = structlog.get_logger()

ProgressCallback = Callable[[str], Coroutine[Any, Any, None]] | None


async def generate_article(
    *,
    job_id: str,
    topic: str,
    instructions: str,
    language: str,
    db: AsyncSession,
    on_progress: ProgressCallback = None,
) -> dict:
    """Run the full generation pipeline and save the result."""
    start = time.monotonic()

    job = await db.get(GenerationJob, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")

    job.status = JobStatus.RUNNING
    await db.flush()

    if on_progress:
        await on_progress("Iniciando geração...")

    try:
        # Fetch RAG context from existing posts (graceful degradation)
        rag_context = ""
        try:
            from app.agents.tools.vector_search import vector_search

            rag_context = await vector_search(query=topic, db=db, limit=5)
            if rag_context and on_progress:
                await on_progress("Contexto de posts anteriores carregado.")
        except Exception:
            logger.warning("rag_context_failed", job_id=job_id)

        initial_state = AgentState(
            topic=topic,
            instructions=instructions,
            language=language,
            rag_context=rag_context,
        )

        if on_progress:
            await on_progress("Pesquisando contexto...")

        # Stream through graph and accumulate final state
        accumulated = initial_state.model_dump()
        async for event in generation_graph.astream(initial_state.model_dump()):
            for node_name, node_output in event.items():
                logger.info("graph_node_completed", node=node_name)
                # Merge node output into accumulated state
                if isinstance(node_output, dict):
                    accumulated.update(node_output)

                if on_progress:
                    progress_messages = {
                        "researcher": "Pesquisa concluída. Redigindo artigo...",
                        "writer": f"Rascunho v{node_output.get('iteration', '?')} pronto. Revisando...",
                        "editor": _editor_progress(node_output),
                        "seo_optimizer": "SEO otimizado. Finalizando...",
                        "publisher": "Artigo pronto!",
                    }
                    msg = progress_messages.get(node_name, f"{node_name} concluído")
                    await on_progress(msg)

        result_state = AgentState(**accumulated)
        duration = int(time.monotonic() - start)

        # Handle slug collision
        repo = PostRepository(db)
        slug = result_state.seo_slug or generate_slug(result_state.topic)
        slug = await _ensure_unique_slug(repo, slug)

        post = await repo.create(
            title=result_state.seo_title or result_state.topic,
            slug=slug,
            excerpt=result_state.seo_description,
            content_mdx=result_state.final_mdx,
            tags=result_state.seo_tags,
            quality_score=result_state.quality_scores.overall,
            language=result_state.language,
            status=PostStatus.DRAFT,
        )

        job.post_id = post.id
        job.status = JobStatus.COMPLETED
        job.quality_scores = result_state.quality_scores.model_dump()
        job.model_usage = result_state.model_usage
        job.prompt_versions = result_state.prompt_versions
        job.iterations = result_state.iteration
        job.duration_seconds = duration
        job.completed_at = datetime.now(UTC)
        await db.commit()

        # Embed after commit — failure doesn't affect the post/job
        try:
            from app.services.embedding_service import embed_post

            await embed_post(post_id=post.id, content=result_state.final_mdx, db=db)
            await db.commit()
        except Exception:
            logger.warning("embed_post_failed_during_generation", post_id=str(post.id))

        logger.info(
            "generation_completed",
            job_id=job_id,
            post_id=str(post.id),
            quality_score=result_state.quality_scores.overall,
            iterations=result_state.iteration,
            duration_seconds=duration,
        )

        return {
            "job_id": job_id,
            "post_id": str(post.id),
            "quality_scores": result_state.quality_scores.model_dump(),
            "iterations": result_state.iteration,
            "duration_seconds": duration,
        }

    except Exception as exc:
        job.status = JobStatus.FAILED
        job.error_message = str(exc)[:500]
        job.duration_seconds = int(time.monotonic() - start)
        await db.commit()
        logger.error("generation_failed", job_id=job_id, error=str(exc))
        raise


async def _ensure_unique_slug(repo: PostRepository, slug: str) -> str:
    """Append -2, -3 etc if slug already exists."""
    original = slug
    counter = 2
    while await repo.get_by_slug(slug):
        slug = f"{original}-{counter}"
        counter += 1
    return slug


def _editor_progress(output: dict) -> str:
    scores = output.get("quality_scores")
    if scores and hasattr(scores, "overall"):
        overall = scores.overall
    elif isinstance(scores, dict):
        overall = scores.get("overall", 0)
    else:
        overall = 0
    approved = output.get("approved", False)
    if approved:
        return f"Score: {overall:.2f} — aprovado!"
    return f"Score: {overall:.2f} — revisando..."
