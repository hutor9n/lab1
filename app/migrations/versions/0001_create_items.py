"""Create the initial items schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the table and adopt databases initialized by the previous job."""
    if sa.inspect(op.get_bind()).has_table("items"):
        return

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(512)),
        sa.Column("price", sa.Float(), nullable=False),
    )
    op.create_index("ix_items_id", "items", ["id"])


def downgrade() -> None:
    """Remove the initial items table."""
    op.drop_table("items")
