from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine, get_db
from app.models import ItemModel

# Автоматичне створення таблиць (якщо міграції не запускалися окремо або для тестів)
if engine.dialect.name == "sqlite":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Items API",
    description="CRUD REST API для управління елементами — Лабораторна робота №4",
    version="2.0.0",
)

# Налаштування CORS для взаємодії з frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic моделі (схеми DTO)
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    """Схема для створення / оновлення елемента."""
    name: str = Field(..., min_length=1, max_length=128, examples=["Laptop"])
    description: Optional[str] = Field(None, max_length=512, examples=["A powerful laptop"])
    price: float = Field(..., gt=0, examples=[999.99])


class Item(ItemCreate):
    """Схема елемента, що повертається клієнту."""
    id: int = Field(..., examples=[1])

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Допоміжна функція для тестів
# ---------------------------------------------------------------------------

def _reset_storage() -> None:
    """Очищає таблицю items у базі даних (використовується в unit-тестах)."""
    db = next(get_db())
    try:
        db.query(ItemModel).delete()
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    """Report whether the API process can serve HTTP."""
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    """Check that the API can query the items schema."""
    try:
        db.query(ItemModel).limit(0).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database schema is unavailable",
        ) from error
    return {"status": "ready"}


# ---------------------------------------------------------------------------
# Ендпоінти CRUD REST API
# ---------------------------------------------------------------------------

@app.get(
    "/api/items",
    response_model=list[Item],
    summary="Отримати список об'єктів",
)
def get_items(db: Session = Depends(get_db)):
    """Повертає список усіх елементів з бази даних."""
    items = db.query(ItemModel).all()
    return items


@app.get(
    "/api/items/{item_id}",
    response_model=Item,
    summary="Отримати об'єкт за ідентифікатором",
)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Повертає елемент за його ID або 404."""
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return item


@app.post(
    "/api/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    summary="Створити новий об'єкт",
)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    """Створює новий елемент у базі даних та повертає його з присвоєним ID."""
    db_item = ItemModel(
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.put(
    "/api/items/{item_id}",
    response_model=Item,
    summary="Оновити наявний об'єкт",
)
def update_item(item_id: int, payload: ItemCreate, db: Session = Depends(get_db)):
    """Оновлює існуючий елемент у базі даних або повертає 404."""
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    db_item.name = payload.name
    db_item.description = payload.description
    db_item.price = payload.price
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete(
    "/api/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити об'єкт",
)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Видаляє елемент із бази даних або повертає 404."""
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    db.delete(db_item)
    db.commit()
    return None
