from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class ItemModel(Base):
    """SQLAlchemy модель таблиці items (Code-First підхід)."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    price = Column(Float, nullable=False)
