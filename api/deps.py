"""Dependency injection for FastAPI routes."""
import logging
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from services.redis_manager import RedisManager

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Optional[Redis] = None
_redis_manager: Optional[RedisManager] = None
_use_mock_redis = False


async def get_redis_client() -> Redis:
    """Get Redis async client."""
    global _redis_client, _use_mock_redis

    if _redis_client is None:
        from dotenv import load_dotenv
        import os

        load_dotenv()

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))

        try:
            # Intentar conectar a Redis real
            _redis_client = await aioredis.from_url(
                f"redis://{redis_host}:{redis_port}",
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2  # Timeout rápido
            )
            await _redis_client.ping()
            logger.info(f"✓ Redis client connected: {redis_host}:{redis_port}")
        except Exception as e:
            # Si falla, usar MockRedis
            logger.warning(f"⚠ Redis not available: {e}")
            logger.info("✓ Using MockRedis for development")
            from services.mock_redis import get_mock_redis
            _redis_client = await get_mock_redis()
            _use_mock_redis = True

    return _redis_client


async def close_redis_client():
    """Close Redis connection."""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        logger.info("Redis client closed")
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

