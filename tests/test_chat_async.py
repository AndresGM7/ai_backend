"""Async tests for chat endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from api.main import app


@pytest.mark.asyncio
async def test_chat_endpoint():
    """Test chat endpoint with mocked LLM."""
    with patch("services.llm_service.LLMService") as mock_llm_class:
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_response.return_value = "This is a test response"
        mock_llm_class.return_value = mock_llm

        # Mock Redis manager
        with patch("api.deps.get_redis_manager") as mock_redis_manager:
            mock_manager = AsyncMock()
            mock_manager.get_conversation_history.return_value = []
            mock_manager.add_message.return_value = None
            mock_redis_manager.return_value = mock_manager

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat",
                    json={
                        "session_id": "test-session",
                        "message": "Hello, AI!"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["session_id"] == "test-session"
                assert data["response"] == "This is a test response"
                assert data["message_count"] == 2


@pytest.mark.asyncio
async def test_get_chat_history():
    """Test retrieving chat history."""
    with patch("api.deps.get_redis_manager") as mock_redis_manager:
        mock_manager = AsyncMock()
        mock_manager.get_conversation_history.return_value = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        mock_redis_manager.return_value = mock_manager

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/chat/history/test-session")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session"
            assert len(data["messages"]) == 2
            assert data["message_count"] == 2


@pytest.mark.asyncio
async def test_clear_chat_history():
    """Test clearing chat history."""
    with patch("api.deps.get_redis_manager") as mock_redis_manager:
        mock_manager = AsyncMock()
        mock_manager.clear_conversation.return_value = None
        mock_redis_manager.return_value = mock_manager

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete("/api/chat/history/test-session")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session"
            assert data["status"] == "cleared"


@pytest.mark.asyncio
async def test_chat_with_history():
    """Test chat endpoint maintains conversation history."""
    with patch("services.llm_service.LLMService") as mock_llm_class:
        mock_llm = AsyncMock()
        mock_llm.generate_response.return_value = "Response based on history"
        mock_llm_class.return_value = mock_llm

        with patch("api.deps.get_redis_manager") as mock_redis_manager:
            mock_manager = AsyncMock()
            mock_manager.get_conversation_history.return_value = [
                {"role": "user", "content": "Previous message"},
                {"role": "assistant", "content": "Previous response"}
            ]
            mock_manager.add_message.return_value = None
            mock_redis_manager.return_value = mock_manager

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat",
                    json={
                        "session_id": "test-session-2",
                        "message": "Follow-up question"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["message_count"] == 4  # 2 previous + 2 new

