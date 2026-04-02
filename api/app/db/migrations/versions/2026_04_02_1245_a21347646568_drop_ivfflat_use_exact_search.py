"""drop IVFFlat index — use exact search for <1000 rows

IVFFlat requires pre-existing data to build cluster lists.
With an empty table, all queries return 0 results.
Exact search (<=> operator without index) is instant for <1000 rows.
Switch to HNSW when row count exceeds ~5000.

Revision ID: a21347646568
Revises: a2d02c93387e
Create Date: 2026-04-02
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a21347646568"
down_revision: str | Sequence[str] | None = "a2d02c93387e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_embeddings_vector")


def downgrade() -> None:
    op.execute(
        "CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10)"
    )
