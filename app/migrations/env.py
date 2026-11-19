"""Configure Alembic using the migration job's database connection."""

from alembic import context

from app.models import Base

context.configure(
    connection=context.config.attributes["connection"],
    target_metadata=Base.metadata,
)
with context.begin_transaction():
    context.run_migrations()
