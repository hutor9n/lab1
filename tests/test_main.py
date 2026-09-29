import pytest
from fastapi.testclient import TestClient

from app.main import app, _reset_storage


@pytest.fixture(autouse=True)
def clean_storage():
    """Очищає in-memory сховище перед кожним тестом."""
    _reset_storage()
    yield
    _reset_storage()


client = TestClient(app)

SAMPLE_ITEM = {"name": "Laptop", "description": "A powerful laptop", "price": 999.99}


# ---------------------------------------------------------------------------
# POST /api/items
# ---------------------------------------------------------------------------

class TestCreateItem:
    def test_create_item_success(self):
        response = client.post("/api/items", json=SAMPLE_ITEM)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == SAMPLE_ITEM["name"]
        assert data["description"] == SAMPLE_ITEM["description"]
        assert data["price"] == SAMPLE_ITEM["price"]

    def test_create_item_minimal(self):
        """Елемент без опису — description необов'язковий."""
        response = client.post("/api/items", json={"name": "Mouse", "price": 25.0})
        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_create_item_invalid_price(self):
        response = client.post("/api/items", json={"name": "Bad", "price": -5})
        assert response.status_code == 422

    def test_create_item_missing_name(self):
        response = client.post("/api/items", json={"price": 10.0})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/items
# ---------------------------------------------------------------------------

class TestGetItems:
    def test_get_items_empty(self):
        response = client.get("/api/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_items_after_create(self):
        client.post("/api/items", json=SAMPLE_ITEM)
        client.post("/api/items", json={"name": "Phone", "price": 499.0})
        response = client.get("/api/items")
        assert response.status_code == 200
        assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# GET /api/items/{id}
# ---------------------------------------------------------------------------

class TestGetItemById:
    def test_get_item_success(self):
        client.post("/api/items", json=SAMPLE_ITEM)
        response = client.get("/api/items/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Laptop"

    def test_get_item_not_found(self):
        response = client.get("/api/items/999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/items/{id}
# ---------------------------------------------------------------------------

class TestUpdateItem:
    def test_update_item_success(self):
        client.post("/api/items", json=SAMPLE_ITEM)
        updated = {"name": "Updated Laptop", "description": "New desc", "price": 1299.99}
        response = client.put("/api/items/1", json=updated)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Laptop"
        assert data["price"] == 1299.99

    def test_update_item_not_found(self):
        response = client.put("/api/items/999", json=SAMPLE_ITEM)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/items/{id}
# ---------------------------------------------------------------------------

class TestDeleteItem:
    def test_delete_item_success(self):
        client.post("/api/items", json=SAMPLE_ITEM)
        response = client.delete("/api/items/1")
        assert response.status_code == 204

        # Перевірити, що елемент видалений
        response = client.get("/api/items/1")
        assert response.status_code == 404

    def test_delete_item_not_found(self):
        response = client.delete("/api/items/999")
        assert response.status_code == 404
