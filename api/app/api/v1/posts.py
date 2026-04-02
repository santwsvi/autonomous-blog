import asyncio
import math
import uuid

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import Auth, PostRepo
from app.models.post import PostStatus
from app.schemas.post import (
    PostCreate,
    PostListPaginated,
    PostListResponse,
    PostResponse,
    PostUpdate,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostListPaginated)
async def list_posts(
    repo: PostRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, pattern=r"^(draft|review|published|archived)$"),
    tag: str | None = None,
    category: str | None = None,
) -> PostListPaginated:
    post_status = PostStatus(status) if status else None
    posts, total = await repo.list(page=page, per_page=per_page, status=post_status, tag=tag, category=category)
    return PostListPaginated(
        items=[PostListResponse.model_validate(p) for p in posts],
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, math.ceil(total / per_page)),
    )


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, repo: PostRepo) -> PostResponse:
    post = await repo.get_by_slug(slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return PostResponse.model_validate(post)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(body: PostCreate, repo: PostRepo, _user: Auth) -> PostResponse:
    existing = await repo.get_by_slug(body.slug)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")

    post = await repo.create(**body.model_dump())
    logger.info("post_created", post_id=str(post.id), slug=post.slug)
    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: uuid.UUID, body: PostUpdate, repo: PostRepo, _user: Auth) -> PostResponse:
    post = await repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        return PostResponse.model_validate(post)

    if "slug" in update_data and update_data["slug"] != post.slug:
        existing = await repo.get_by_slug(update_data["slug"])
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")

    was_draft = post.status != PostStatus.PUBLISHED
    post = await repo.update(post, **update_data)

    # Auto-embed in background when publishing (non-blocking)
    is_now_published = post.status == PostStatus.PUBLISHED
    content_changed = "content_mdx" in update_data
    if is_now_published and (was_draft or content_changed):
        _schedule_embedding(str(post.id), post.content_mdx)

    logger.info("post_updated", post_id=str(post.id))
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: uuid.UUID, repo: PostRepo, _user: Auth) -> None:
    post = await repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await repo.delete(post)
    logger.info("post_deleted", post_id=str(post.id))


# --- Background embedding ---

_bg_tasks: set[asyncio.Task] = set()


def _schedule_embedding(post_id: str, content: str) -> None:
    """Fire-and-forget embedding — doesn't block the HTTP response."""
    task = asyncio.create_task(_embed_in_background(post_id, content))
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


async def _embed_in_background(post_id: str, content: str) -> None:
    from app.db.session import async_session
    from app.services.embedding_service import embed_post

    try:
        async with async_session() as db:
            await embed_post(post_id=uuid.UUID(post_id), content=content, db=db)
            await db.commit()
            logger.info("post_embedded_background", post_id=post_id)
    except Exception:
        logger.exception("post_embed_background_failed", post_id=post_id)
