import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect, text


def test_migration_creates_schema_and_can_be_rerun(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'migration.db').as_posix()}"
    environment = dict(os.environ, DATABASE_URL=database_url)
    command = [sys.executable, "-m", "app.migrate"]

    subprocess.run(command, env=environment, check=True)
    engine = create_engine(database_url)
    assert inspect(engine).has_table("items")
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO items (name, price) VALUES ('Book', 5)"))

    subprocess.run(command, env=environment, check=True)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT name FROM items")) == "Book"
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0001"
    engine.dispose()
