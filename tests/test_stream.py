"""Tests para streaming endpoints - Día 3."""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_stream_endpoint_exists():
    """Test que el endpoint de streaming existe."""
    response = client.get("/api/stream")
    assert response.status_code == 200


def test_stream_returns_text():
    """Test que el streaming retorna texto."""
    response = client.get("/api/stream")

    # Leer el contenido del stream
    content = response.text

    assert len(content) > 0
    assert "Hola" in content or "streaming" in content


def test_stream_content_type():
    """Test que el content type es correcto para streaming."""
    response = client.get("/api/stream")

    # Streaming de texto plano
    assert "text/plain" in response.headers.get("content-type", "")


def test_stream_json_endpoint():
    """Test del endpoint de streaming JSON."""
    response = client.get("/api/stream-json")

    assert response.status_code == 200
    content = response.text

    # Verificar que contiene eventos JSON
    assert "data:" in content
    assert "event" in content


def test_stream_json_content_type():
    """Test que el content type es SSE para JSON streaming."""
    response = client.get("/api/stream-json")

    content_type = response.headers.get("content-type", "")
    assert "text/event-stream" in content_type
