"""Redis manager for session and conversation storage - Día 2."""
import os
import json
from typing import Any, Dict, List, Optional

import redis
from redis.asyncio import Redis

# Configuración de Redis desde variables de entorno
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Cliente Redis síncrono (para funciones simples del Día 2)
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True,
        socket_connect_timeout=5
    )
    r.ping()
    print(f"✓ Redis conectado en {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    print(f"⚠ Redis no disponible, usando MockRedis: {e}")
    # Fallback a MockRedis
    from services.mock_redis import MockRedis
    r = MockRedis()


def save_session(user_id: str, message: Dict[str, Any], ttl: int = 3600):
    """
    Guarda la sesión del usuario en Redis con TTL.

    Args:
        user_id: Identificador único del usuario
        message: Diccionario con datos de la sesión
        ttl: Tiempo de vida en segundos (por defecto 1 hora)
    """
    try:
        r.setex(user_id, ttl, json.dumps(message))
    except Exception as e:
        # Para MockRedis que no tiene setex síncrono
        r.set(user_id, json.dumps(message))


def get_session(user_id: str) -> Dict[str, Any]:
    """
    Recupera la sesión del usuario desde Redis.

    Args:
        user_id: Identificador único del usuario

    Returns:
        Diccionario con datos de la sesión o diccionario vacío si no existe
    """
    try:
        data = r.get(user_id)
        return json.loads(data) if data else {}
    except Exception:
        return {}


# ============================================
# Clase RedisManager avanzada (para uso futuro)
# ============================================

class RedisManager:
    """Manages Redis operations for sessions and conversations."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.conversation_prefix = "conversation:"
        self.cache_prefix = "cache:"
        self.default_ttl = 3600  # 1 hour

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """Add a message to conversation history."""
        key = f"{self.conversation_prefix}{session_id}"
        message = {
            "role": role,
            "content": content
        }

        await self.redis.rpush(key, json.dumps(message))
        await self.redis.expire(key, self.default_ttl * 24)  # 24 hours

    async def get_conversation_history(
        self,
        session_id: str
    ) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        key = f"{self.conversation_prefix}{session_id}"
        messages = await self.redis.lrange(key, 0, -1)

        return [json.loads(msg) for msg in messages]

    async def clear_conversation(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        key = f"{self.conversation_prefix}{session_id}"
        await self.redis.delete(key)

    async def set_cache(
        self,
        cache_key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set a cached value."""
        key = f"{self.cache_prefix}{cache_key}"

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        await self.redis.set(key, value, ex=ttl or self.default_ttl)

    async def get_cache(self, cache_key: str) -> Optional[str]:
        """Get a cached value."""
        key = f"{self.cache_prefix}{cache_key}"
        value = await self.redis.get(key)

        if value and value.startswith(("{", "[")):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        return value

    async def delete_cache(self, cache_key: str) -> None:
        """Delete a cached value."""
        key = f"{self.cache_prefix}{cache_key}"
        await self.redis.delete(key)

    async def get_session_count(self) -> int:
        """Get total number of active sessions."""
        pattern = f"{self.conversation_prefix}*"
        keys = await self.redis.keys(pattern)
        return len(keys)
