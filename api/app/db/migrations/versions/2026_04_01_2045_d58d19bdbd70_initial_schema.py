"""initial_schema

Revision ID: d58d19bdbd70
Revises:
Create Date: 2026-04-01

"""

from collections.abc import Sequence

from alembic import op

revision: str = "d58d19bdbd70"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


STATEMENTS_UP = [
    "CREATE TYPE post_status AS ENUM ('draft', 'review', 'published', 'archived')",
    "CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed')",
    """CREATE TABLE posts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title VARCHAR(255) NOT NULL,
        slug VARCHAR(255) UNIQUE NOT NULL,
        excerpt TEXT,
        content_mdx TEXT NOT NULL CONSTRAINT ck_posts_content_mdx_max_length CHECK (length(content_mdx) <= 100000),
        status post_status NOT NULL DEFAULT 'draft',
        quality_score NUMERIC(3,2) CONSTRAINT ck_posts_quality_score_range CHECK (quality_score IS NULL OR (quality_score >= 0.00 AND quality_score <= 1.00)),
        seo_meta JSONB,
        tags TEXT[],
        category VARCHAR(100),
        reading_time_minutes INTEGER,
        word_count INTEGER CONSTRAINT ck_posts_word_count_positive CHECK (word_count IS NULL OR word_count >= 0),
        language VARCHAR(10) NOT NULL DEFAULT 'pt-BR',
        featured BOOLEAN NOT NULL DEFAULT false,
        published_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    "CREATE INDEX idx_posts_status ON posts(status)",
    "CREATE INDEX idx_posts_published_at ON posts(published_at DESC) WHERE status = 'published'",
    "CREATE INDEX idx_posts_slug ON posts(slug)",
    "CREATE INDEX idx_posts_tags ON posts USING GIN(tags)",
    "CREATE INDEX idx_posts_category ON posts(category)",
    """CREATE TABLE generation_jobs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        post_id UUID,
        prompt TEXT NOT NULL CONSTRAINT ck_generation_jobs_prompt_max_length CHECK (length(prompt) <= 5000),
        status job_status NOT NULL DEFAULT 'pending',
        model_usage JSONB,
        quality_scores JSONB,
        prompt_versions JSONB,
        iterations INTEGER NOT NULL DEFAULT 0 CONSTRAINT ck_generation_jobs_max_iterations CHECK (iterations <= 5),
        duration_seconds INTEGER,
        error_message TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        completed_at TIMESTAMPTZ
    )""",
    "CREATE INDEX idx_generation_jobs_status ON generation_jobs(status)",
    """CREATE TABLE embeddings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        post_id UUID NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_text TEXT NOT NULL CONSTRAINT ck_embeddings_chunk_text_max_length CHECK (length(chunk_text) <= 5000),
        vector_id VARCHAR(255) NOT NULL,
        token_count INTEGER,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(post_id, chunk_index)
    )""",
    "CREATE INDEX idx_embeddings_post ON embeddings(post_id)",
    """CREATE TABLE page_views (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        post_id UUID NOT NULL,
        visitor_hash VARCHAR(64),
        referrer VARCHAR(500),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    "CREATE INDEX idx_page_views_post_date ON page_views(post_id, created_at DESC)",
    "CREATE INDEX idx_page_views_created ON page_views(created_at DESC)",
]

STATEMENTS_DOWN = [
    "DROP TABLE IF EXISTS page_views",
    "DROP TABLE IF EXISTS embeddings",
    "DROP TABLE IF EXISTS generation_jobs",
    "DROP TABLE IF EXISTS posts",
    "DROP TYPE IF EXISTS job_status",
    "DROP TYPE IF EXISTS post_status",
]


def upgrade() -> None:
    for stmt in STATEMENTS_UP:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in STATEMENTS_DOWN:
        op.execute(stmt)
