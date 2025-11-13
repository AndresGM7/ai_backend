"""Dependency injection for FastAPI routes."""
import logging
from typing import Optional

from services.redis_manager import RedisManager

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Optional[object] = None
_redis_manager: Optional[RedisManager] = None


async def get_redis_client():
    """Get Redis async client (usando MockRedis para desarrollo)."""
    global _redis_client

    if _redis_client is None:
        # Usar directamente MockRedis para evitar problemas de conexión
        logger.info("✓ Usando MockRedis para desarrollo")
        from services.mock_redis import get_mock_redis
        _redis_client = await get_mock_redis()

    return _redis_client


async def close_redis_client():
    """Close Redis connection."""
    global _redis_client

    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("Redis client closed")
        except Exception:
            pass
        _redis_client = None


async def get_redis_manager() -> RedisManager:
    """Get Redis manager instance."""
    global _redis_manager

    if _redis_manager is None:
        redis_client = await get_redis_client()
        _redis_manager = RedisManager(redis_client)

    return _redis_manager


def get_logger(name: str) -> logging.Logger:
    """Get configured logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
