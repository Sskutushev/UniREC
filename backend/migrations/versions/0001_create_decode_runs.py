"""create decode runs table

Revision ID: 0001_create_decode_runs
Revises:
Create Date: 2026-06-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_decode_runs"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    run_status = sa.Enum("pending", "running", "completed", "failed", name="run_status")

    op.create_table(
        "decode_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("status", run_status, nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw_provider_output", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("provider_name", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_decode_runs_input_hash", "decode_runs", ["input_hash"], unique=False)
    op.create_index("ix_decode_runs_status", "decode_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_decode_runs_status", table_name="decode_runs")
    op.drop_index("ix_decode_runs_input_hash", table_name="decode_runs")
    op.drop_table("decode_runs")
