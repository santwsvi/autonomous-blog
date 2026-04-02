"""Generation API — trigger article generation and stream progress via SSE."""

import asyncio
import uuid

import structlog
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import Auth, Db
from app.models.post import GenerationJob
from app.schemas.generation import GenerationCreate, GenerationResponse
from app.services.generation_service import generate_article

logger = structlog.get_logger()
router = APIRouter(prefix="/generate", tags=["generation"])

# In-memory progress store (per-job). In production, use Redis pub/sub.
_progress: dict[str, asyncio.Queue] = {}


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_generation(body: GenerationCreate, db: Db, _user: Auth) -> dict:
    """Start article generation. Returns job_id and stream_token."""
    job = GenerationJob(prompt=body.prompt)
    db.add(job)
    await db.flush()
    await db.refresh(job)
    await db.commit()

    job_id = str(job.id)

    # Create progress queue for SSE
    _progress[job_id] = asyncio.Queue()

    # Start generation in background (store ref to prevent GC)
    _tasks: set = getattr(create_generation, "_tasks", set())
    task = asyncio.create_task(_run_generation(job_id=job_id, prompt=body.prompt, db_url=None))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    create_generation._tasks = _tasks  # type: ignore[attr-defined]

    logger.info("generation_started", job_id=job_id)

    return {
        "job_id": job_id,
        "stream_url": f"/api/v1/generate/{job_id}/stream",
    }


@router.get("/{job_id}/stream")
async def stream_progress(job_id: str, _user: Auth) -> StreamingResponse:
    """SSE endpoint — streams generation progress."""
    queue = _progress.get(job_id)

    async def event_stream():
        if queue is None:
            yield 'data: {"status": "error", "message": "Job not found"}\n\n'
            return

        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=300)
                except TimeoutError:
                    yield 'data: {"status": "timeout"}\n\n'
                    break

                yield f"data: {msg}\n\n"

                if '"done"' in msg or '"error"' in msg:
                    break
        finally:
            _progress.pop(job_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{job_id}", response_model=GenerationResponse)
async def get_generation(job_id: str, db: Db) -> GenerationResponse:
    """Get generation job status."""
    try:
        uid = uuid.UUID(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid job ID") from exc

    job = await db.get(GenerationJob, uid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return GenerationResponse.model_validate(job)


async def _run_generation(*, job_id: str, prompt: str, db_url: str | None) -> None:
    """Background task that runs the generation pipeline."""
    import json

    from app.db.session import async_session

    queue = _progress.get(job_id)

    async def on_progress(message: str) -> None:
        if queue:
            await queue.put(json.dumps({"status": "progress", "message": message}))

    try:
        async with async_session() as db:
            result = await generate_article(
                job_id=job_id,
                topic=prompt,
                instructions="",
                language="pt-BR",
                db=db,
                on_progress=on_progress,
            )
            if queue:
                await queue.put(json.dumps({"status": "done", "result": result}))
    except Exception as exc:
        logger.error("generation_background_error", job_id=job_id, error=str(exc))
        if queue:
            await queue.put(json.dumps({"status": "error", "message": str(exc)[:200]}))
