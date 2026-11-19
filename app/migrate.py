"""Консольний застосунок (Migration Job) для застосування міграцій до бази даних."""
import sys
import os
import time

# Додаємо кореневу директорію проєкту до sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, Base, DATABASE_URL
from app.models import ItemModel


def apply_migrations():
    print("==================================================")
    print("        DATABASE MIGRATION JOB STARTING          ")
    print("==================================================")
    print(f"Target Database URL: {DATABASE_URL}")

    # Retry механізм очікування готовності бази даних (наприклад, PostgreSQL у Kubernetes)
    max_retries = 30
    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Attempt {attempt}/{max_retries}] Connecting to database...")
            with engine.connect() as conn:
                print("Connection successfully established!")
                break
        except Exception as e:
            print(f"Database not ready yet ({e}). Retrying in {retry_delay}s...")
            if attempt == max_retries:
                print("ERROR: Could not connect to the database after maximum retries.")
                sys.exit(1)
            time.sleep(retry_delay)

    print("Applying Code-First schema migrations (Base.metadata.create_all)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables verified / created:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        print("MIGRATION COMPLETED SUCCESSFULLY!")
    except Exception as e:
        print(f"ERROR: Migration failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    apply_migrations()
