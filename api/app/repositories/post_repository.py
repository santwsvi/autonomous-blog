import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostStatus


class PostRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, post_id: uuid.UUID) -> Post | None:
        return await self._db.get(Post, post_id)

    async def get_by_slug(self, slug: str) -> Post | None:
        result = await self._db.execute(select(Post).where(Post.slug == slug))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        status: PostStatus | None = None,
        tag: str | None = None,
        category: str | None = None,
    ) -> tuple[list[Post], int]:
        query: Select = select(Post)

        if status is not None:
            query = query.where(Post.status == status)
        if tag is not None:
            query = query.where(Post.tags.any(tag))
        if category is not None:
            query = query.where(Post.category == category)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Post.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self._db.execute(query)
        posts = list(result.scalars().all())

        return posts, total

    async def create(self, **kwargs: object) -> Post:
        post = Post(**kwargs)
        self._estimate_reading_time(post)
        self._db.add(post)
        await self._db.flush()
        await self._db.refresh(post)
        return post

    async def update(self, post: Post, **kwargs: object) -> Post:
        for key, value in kwargs.items():
            if value is not None:
                setattr(post, key, value)

        if "content_mdx" in kwargs and kwargs["content_mdx"] is not None:
            self._estimate_reading_time(post)

        if kwargs.get("status") == "published" and post.published_at is None:
            post.published_at = datetime.now(UTC)

        post.updated_at = datetime.now(UTC)
        await self._db.flush()
        await self._db.refresh(post)
        return post

    async def delete(self, post: Post) -> None:
        await self._db.delete(post)
        await self._db.flush()

    def _estimate_reading_time(self, post: Post) -> None:
        words = len(post.content_mdx.split())
        post.word_count = words
        post.reading_time_minutes = max(1, math.ceil(words / 200))
