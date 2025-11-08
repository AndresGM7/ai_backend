"""Tests para métricas de latencia - Día 5."""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_metrics_endpoint_exists():
    """Test que el endpoint de métricas existe."""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_structure():
    """Test que las métricas tienen la estructura correcta."""
    # Hacer algunos requests primero para generar métricas
    for _ in range(15):
        client.get("/status")

    # Obtener métricas
    response = client.get("/metrics")
    data = response.json()

    assert "latency_ms" in data
    assert "total_requests" in data
    assert "status" in data

    latency = data["latency_ms"]
    assert "p50" in latency
    assert "p95" in latency
    assert "p99" in latency
    assert "avg" in latency


def test_latency_header_present():
    """Test que el header X-Process-Time está presente."""
    response = client.get("/status")

    assert "X-Process-Time" in response.headers
    assert "ms" in response.headers["X-Process-Time"]


def test_metrics_after_multiple_requests():
    """Test que las métricas se actualizan correctamente."""
    # Limpiar métricas anteriores haciendo muchos requests
    for _ in range(20):
        client.get("/status")
        client.get("/api/stream")

    response = client.get("/metrics")
    data = response.json()

    # Verificar que tenemos suficientes requests
    assert data["total_requests"] >= 20

    # Verificar que los percentiles son razonables (< 1 segundo)
    assert data["latency_ms"]["p95"] < 1000
    assert data["latency_ms"]["p50"] < data["latency_ms"]["p95"]


def test_health_status_based_on_latency():
    """Test que el status cambia según la latencia."""
    response = client.get("/metrics")
    data = response.json()

    # El status debería ser "healthy" o "degraded"
    assert data["status"] in ["healthy", "degraded"]

    # Si P95 < 300ms, debería ser healthy
    if data["latency_ms"]["p95"] < 300:
        assert data["status"] == "healthy"
"""Tests para validación Pydantic - Día 4."""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_chat_with_valid_request():
    """Test que la validación Pydantic acepta requests válidos."""
    response = client.post(
        "/api/chat/user123",
        json={"message": "Test message"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_len" in data
    assert "user_id" in data
    assert data["user_id"] == "user123"


def test_chat_with_empty_message():
    """Test que la validación rechaza mensajes vacíos."""
    response = client.post(
        "/api/chat/user123",
        json={"message": ""}
    )

    assert response.status_code == 422  # Validation error


def test_chat_with_missing_message():
    """Test que la validación requiere el campo message."""
    response = client.post(
        "/api/chat/user123",
        json={}
    )

    assert response.status_code == 422  # Validation error


def test_chat_with_very_long_message():
    """Test que la validación limita la longitud del mensaje."""
    long_message = "x" * 1001  # Más de 1000 caracteres
    response = client.post(
        "/api/chat/user123",
        json={"message": long_message}
    )

    assert response.status_code == 422  # Validation error


def test_status_returns_typed_response():
    """Test que /status retorna la estructura tipada correcta."""
    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()

    # Verificar estructura del StatusResponse
    required_fields = ["status", "message", "project", "week", "features"]
    for field in required_fields:
        assert field in data

    assert isinstance(data["features"], list)
    assert data["week"] == 1


def test_openapi_schema_includes_models():
    """Test que el schema OpenAPI incluye los modelos Pydantic."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Verificar que los modelos están en el schema
    assert "components" in schema
    assert "schemas" in schema["components"]

    # Verificar que ChatRequest está definido
    schemas = schema["components"]["schemas"]
    assert "ChatRequest" in schemas or "Body_chat" in str(schemas)

