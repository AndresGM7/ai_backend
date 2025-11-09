"""
Redis Mock para desarrollo sin Redis instalado
Este módulo simula Redis para desarrollo local cuando no tienes Redis disponible
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re


class MockRedis:
    """Mock de Redis (API síncrona compatible con redis-py)."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, datetime] = {}

    # Métodos síncronos
    def ping(self) -> bool:
        return True

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._data[key] = value
        if ex:
            self._expiry[key] = datetime.now() + timedelta(seconds=ex)
        return True

    def setex(self, key: str, time: int, value: Any) -> bool:
        self._data[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=time)
        return True

    def get(self, key: str) -> Optional[str]:
        if key in self._expiry and datetime.now() > self._expiry[key]:
            # Expirado
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return None
        return self._data.get(key)

    def delete(self, key: str) -> int:
        existed = 1 if key in self._data else 0
        self._data.pop(key, None)
        self._expiry.pop(key, None)
        return existed

    def keys(self, pattern: str) -> List[str]:
        pattern_regex = pattern.replace('*', '.*')
        return [k for k in self._data.keys() if re.match(pattern_regex, k)]


class AsyncMockRedis:
    """Mock de Redis (API asíncrona compatible con redis.asyncio)."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, datetime] = {}

    # Métodos asíncronos
    async def ping(self) -> bool:
        return True

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._data[key] = value
        if ex:
            self._expiry[key] = datetime.now() + timedelta(seconds=ex)
        return True

    async def get(self, key: str) -> Optional[str]:
        if key in self._expiry and datetime.now() > self._expiry[key]:
            # Expirado
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return None
        return self._data.get(key)

    async def delete(self, key: str) -> int:
        existed = 1 if key in self._data else 0
        self._data.pop(key, None)
        self._expiry.pop(key, None)
        return existed

    async def rpush(self, key: str, *values) -> int:
        if key not in self._data:
            self._data[key] = []
        self._data[key].extend(values)
        return len(self._data[key])

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        if key not in self._data:
            return []
        lst = self._data[key]
        if end == -1:
            return lst[start:]
        return lst[start:end + 1]

    async def keys(self, pattern: str) -> List[str]:
        pattern_regex = pattern.replace('*', '.*')
        return [k for k in self._data.keys() if re.match(pattern_regex, k)]

    async def expire(self, key: str, seconds: int) -> bool:
        if key in self._data:
            self._expiry[key] = datetime.now() + timedelta(seconds=seconds)
            return True
        return False

    async def close(self):
        pass


async def get_mock_redis():
    """Retorna una instancia de AsyncMockRedis."""
    return AsyncMockRedis()
