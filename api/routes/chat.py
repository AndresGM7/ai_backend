"""Chat routes: session management with Redis and Pydantic validation."""
from fastapi import APIRouter, HTTPException
import logging

from services.redis_manager import save_session, get_session
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger("ai_backend")


@router.post("/chat/{user_id}", response_model=ChatResponse)
async def chat(user_id: str, chat_request: ChatRequest):
    """
    Chat endpoint with session persistence in Redis and Pydantic validation.

    Args:
        user_id: Unique user identifier
        chat_request: Validated request model

    Returns:
        Typed ChatResponse
    """
    try:
        # Recuperar sesión existente
        session = get_session(user_id)
        logger.info(f"Session retrieved for user: {user_id}")

        # Agregar mensaje al historial
        session.setdefault("history", []).append({
            "role": "user",
            "text": chat_request.message
        })

        # Guardar sesión actualizada (TTL: 1 hora)
        save_session(user_id, session, ttl=3600)
        logger.info(f"Session saved for user: {user_id}, history length: {len(session['history'])}")

        return ChatResponse(
            response=f"Mensaje guardado para usuario {user_id}",
            session_len=len(session["history"]),
            user_id=user_id
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar mensaje: {str(e)}")


@router.get("/chat/{user_id}/history")
async def get_chat_history(user_id: str):
    """Get full chat history for a user."""
    try:
        session = get_session(user_id)
        history = session.get("history", [])

        return {
            "user_id": user_id,
            "history": history,
            "message_count": len(history)
        }

    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")


@router.delete("/chat/{user_id}/history")
async def clear_chat_history(user_id: str):
    """Clear a user's chat history."""
    try:
        # Guardar sesión vacía
        save_session(user_id, {}, ttl=1)  # TTL corto para eliminar pronto
        logger.info(f"Session cleared for user: {user_id}")

        return {
            "user_id": user_id,
            "status": "cleared",
            "message": "Historial eliminado correctamente"
        }

    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=f"Error al limpiar historial: {str(e)}")
