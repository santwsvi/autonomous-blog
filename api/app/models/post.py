import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PostStatus(enum.StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint("length(content_mdx) <= 100000", name="content_mdx_max_length"),
        CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0.00 AND quality_score <= 1.00)",
            name="quality_score_range",
        ),
        CheckConstraint("word_count IS NULL OR word_count >= 0", name="word_count_positive"),
        Index("idx_posts_published_at", "published_at", postgresql_where=text("status = 'published'")),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text)
    content_mdx: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status", create_type=False, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=PostStatus.DRAFT,
        server_default="draft",
    )
    quality_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
    seo_meta: Mapped[dict | None] = mapped_column(JSONB)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    category: Mapped[str | None] = mapped_column(String(100))
    reading_time_minutes: Mapped[int | None] = mapped_column()
    word_count: Mapped[int | None] = mapped_column()
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="pt-BR", server_default="pt-BR")
    featured: Mapped[bool] = mapped_column(default=False, server_default="false")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()"), onupdate=text("NOW()")
    )


class JobStatus(enum.StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    __table_args__ = (
        CheckConstraint("length(prompt) <= 5000", name="prompt_max_length"),
        CheckConstraint("iterations <= 5", name="max_iterations"),
    )

    post_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", create_type=False, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=JobStatus.PENDING,
        server_default="pending",
    )
    model_usage: Mapped[dict | None] = mapped_column(JSONB)
    quality_scores: Mapped[dict | None] = mapped_column(JSONB)
    prompt_versions: Mapped[dict | None] = mapped_column(JSONB)
    iterations: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    duration_seconds: Mapped[int | None] = mapped_column()
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = (CheckConstraint("length(chunk_text) <= 5000", name="chunk_text_max_length"),)

    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(255), nullable=False)
    token_count: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class PageView(Base):
    __tablename__ = "page_views"

    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    visitor_hash: Mapped[str | None] = mapped_column(String(64))
    referrer: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
