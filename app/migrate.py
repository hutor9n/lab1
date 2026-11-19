"""Apply the database schema revisions."""

import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.exc import OperationalError

from app.database import engine


def main() -> None:
    """Wait for the database, then upgrade its schema."""
    config = Config()
    config.set_main_option(
        "script_location", Path(__file__).with_name("migrations").as_posix()
    )

    for attempt in range(30):
        try:
            connection = engine.connect()
            break
        except OperationalError:
            if attempt == 29:
                raise
            print("Waiting for the database...", flush=True)
            time.sleep(2)

    with connection, connection.begin():
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    print("Database schema is up to date.", flush=True)


if __name__ == "__main__":
    main()
