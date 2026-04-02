"""add pgvector extension, embedding vector column, and FK on generation_jobs

Revision ID: a2d02c93387e
Revises: d58d19bdbd70
Create Date: 2026-04-02
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a2d02c93387e"
down_revision: str | Sequence[str] | None = "d58d19bdbd70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATEMENTS_UP = [
    # pgvector extension (requires superuser — run manually if needed)
    "CREATE EXTENSION IF NOT EXISTS vector",
    # Add vector column to embeddings
    "ALTER TABLE embeddings ADD COLUMN embedding vector(1536)",
    # Index for cosine similarity search
    "CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10)",
    # FK on generation_jobs.post_id (missing from initial schema)
    "ALTER TABLE generation_jobs ADD CONSTRAINT fk_generation_jobs_post_id FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE SET NULL",
]

STATEMENTS_DOWN = [
    "ALTER TABLE generation_jobs DROP CONSTRAINT IF EXISTS fk_generation_jobs_post_id",
    "DROP INDEX IF EXISTS idx_embeddings_vector",
    "ALTER TABLE embeddings DROP COLUMN IF EXISTS embedding",
    "DROP EXTENSION IF EXISTS vector",
]


def upgrade() -> None:
    for stmt in STATEMENTS_UP:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in STATEMENTS_DOWN:
        op.execute(stmt)
