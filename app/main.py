from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="Items API",
    description="CRUD REST API для управління елементами — Лабораторна робота №1",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Модель даних
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    """Схема для створення / оновлення елемента."""
    name: str = Field(..., min_length=1, max_length=128, examples=["Laptop"])
    description: Optional[str] = Field(None, max_length=512, examples=["A powerful laptop"])
    price: float = Field(..., gt=0, examples=[999.99])


class Item(ItemCreate):
    """Схема елемента, що повертається клієнту."""
    id: int = Field(..., examples=[1])


# ---------------------------------------------------------------------------
# In-memory сховище
# ---------------------------------------------------------------------------

_items: dict[int, Item] = {}
_next_id: int = 1


def _reset_storage() -> None:
    """Очищає сховище (використовується в тестах)."""
    global _items, _next_id
    _items = {}
    _next_id = 1


# ---------------------------------------------------------------------------
# Ендпоінти
# ---------------------------------------------------------------------------

@app.get(
    "/api/items",
    response_model=list[Item],
    summary="Отримати список об'єктів",
)
def get_items():
    """Повертає список усіх елементів."""
    return list(_items.values())


@app.get(
    "/api/items/{item_id}",
    response_model=Item,
    summary="Отримати об'єкт за ідентифікатором",
)
def get_item(item_id: int):
    """Повертає елемент за його ID або 404."""
    item = _items.get(item_id)
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
def create_item(payload: ItemCreate):
    """Створює новий елемент та повертає його з присвоєним ID."""
    global _next_id
    item = Item(id=_next_id, **payload.model_dump())
    _items[_next_id] = item
    _next_id += 1
    return item


@app.put(
    "/api/items/{item_id}",
    response_model=Item,
    summary="Оновити наявний об'єкт",
)
def update_item(item_id: int, payload: ItemCreate):
    """Оновлює існуючий елемент або повертає 404."""
    if item_id not in _items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    updated = Item(id=item_id, **payload.model_dump())
    _items[item_id] = updated
    return updated


@app.delete(
    "/api/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити об'єкт",
)
def delete_item(item_id: int):
    """Видаляє елемент за ID або повертає 404."""
    if item_id not in _items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    del _items[item_id]
