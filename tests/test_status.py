"""Tests para el endpoint de status."""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_status_endpoint_success():
    """Test que el endpoint de status funciona correctamente."""
    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "Price Optimization System"


def test_status_contains_features():
    """Test que el status incluye la lista de features."""
    response = client.get("/status")
    data = response.json()

    assert "features" in data
    assert isinstance(data["features"], list)
    assert "chat" in data["features"]
    assert "streaming" in data["features"]


def test_status_response_structure():
    """Test que la respuesta tiene la estructura correcta."""
    response = client.get("/status")
    data = response.json()

    required_fields = ["status", "message", "project", "week"]
    for field in required_fields:
        assert field in data, f"Campo '{field}' faltante en respuesta"


def test_root_endpoint():
    """Test del endpoint raíz (si existe)."""
    response = client.get("/")
    # Puede retornar 404 si no está implementado, eso está bien
    assert response.status_code in [200, 404]
