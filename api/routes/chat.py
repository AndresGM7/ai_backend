"""Chat routes - Día 2: Session management con Redis."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from services.redis_manager import save_session, get_session

router = APIRouter()
logger = logging.getLogger("ai_backend")


class ChatMessage(BaseModel):
    """Modelo para mensaje de chat."""
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "¿Cuál es el precio óptimo para mi producto?"
            }
        }


@router.post("/chat/{user_id}")
async def chat(user_id: str, chat_message: ChatMessage):
    """
    Endpoint de chat con persistencia de sesión en Redis.

    Día 2: Implementa session management básico con Redis.
    - Guarda el historial de conversación por usuario
    - TTL de 1 hora por sesión
    - Permite rastrear contexto de conversación

    Args:
        user_id: Identificador único del usuario
        chat_message: Mensaje del usuario

    Returns:
        Respuesta con confirmación y longitud de historial
    """
    try:
        # Recuperar sesión existente
        session = get_session(user_id)
        logger.info(f"Session retrieved for user: {user_id}")

        # Agregar mensaje al historial
        session.setdefault("history", []).append({
            "role": "user",
            "text": chat_message.message
        })

        # Guardar sesión actualizada (TTL: 1 hora)
        save_session(user_id, session, ttl=3600)
        logger.info(f"Session saved for user: {user_id}, history length: {len(session['history'])}")

        return {
            "response": f"Mensaje guardado para usuario {user_id}",
            "session_len": len(session["history"]),
            "user_id": user_id,
            "message_received": chat_message.message
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar mensaje: {str(e)}")


@router.get("/chat/{user_id}/history")
async def get_chat_history(user_id: str):
    """
    Obtiene el historial de chat de un usuario.

    Args:
        user_id: Identificador único del usuario

    Returns:
        Historial completo de la sesión
    """
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
    """
    Limpia el historial de chat de un usuario.

    Args:
        user_id: Identificador único del usuario

    Returns:
        Confirmación de eliminación
    """
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

