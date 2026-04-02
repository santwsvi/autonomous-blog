import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    excerpt: str | None = None
    content_mdx: str = Field(..., min_length=1, max_length=100000)
    tags: list[str] = Field(default_factory=list)
    category: str | None = Field(None, max_length=100)
    language: str = Field("pt-BR", max_length=10)
    featured: bool = False

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        return [tag.strip().lower() for tag in v if tag.strip()]


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    excerpt: str | None = None
    content_mdx: str | None = Field(None, min_length=1, max_length=100000)
    status: str | None = Field(None, pattern=r"^(draft|review|published|archived)$")
    tags: list[str] | None = None
    category: str | None = Field(None, max_length=100)
    language: str | None = Field(None, max_length=10)
    featured: bool | None = None
    seo_meta: dict | None = None


class PostResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    slug: str
    excerpt: str | None
    content_mdx: str
    status: str
    quality_score: float | None
    seo_meta: dict | None
    tags: list[str]
    category: str | None
    reading_time_minutes: int | None
    word_count: int | None
    language: str
    featured: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    slug: str
    excerpt: str | None
    status: str
    tags: list[str]
    category: str | None
    reading_time_minutes: int | None
    language: str
    featured: bool
    published_at: datetime | None
    created_at: datetime


class PostListPaginated(BaseModel):
    items: list[PostListResponse]
    total: int
    page: int
    per_page: int
    pages: int
