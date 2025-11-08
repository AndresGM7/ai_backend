"""Tests for status endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Backend API"
    assert "docs" in data
    assert "health" in data


def test_status_endpoint():
    """Test status endpoint."""
    response = client.get("/api/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"
    assert data["service"] == "ai_backend"


@pytest.mark.asyncio
async def test_health_check_success():
    """Test health check with successful Redis connection."""
    with patch("api.deps.get_redis_client") as mock_redis:
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["redis"] == "connected"


@pytest.mark.asyncio
async def test_health_check_redis_failure():
    """Test health check when Redis is unavailable."""
    with patch("api.deps.get_redis_client") as mock_redis:
        mock_redis.side_effect = Exception("Redis connection failed")

        response = client.get("/api/health")

        # Note: This test may need adjustment based on actual error handling
        assert response.status_code in [503, 500]

