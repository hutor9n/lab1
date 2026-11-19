import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Отримуємо ConnectionString зі змінної середовища.
# За замовчуванням для локальних тестів використовується SQLite in-memory,
# а для середовища Kubernetes / Docker — PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./items.db")

# Для SQLite потрібен connect_args={"check_same_thread": False}
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency для отримання сесії бази даних у FastAPI ендпоінтах."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
