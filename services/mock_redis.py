"""
Redis Mock para desarrollo sin Redis instalado
Este módulo simula Redis para desarrollo local cuando no tienes Redis disponible
"""
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta


class MockRedis:
    """Mock de Redis para desarrollo local"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, datetime] = {}

    async def ping(self) -> bool:
        """Simula ping de Redis"""
        return True

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Simula SET de Redis"""
        self._data[key] = value
        if ex:
            self._expiry[key] = datetime.now() + timedelta(seconds=ex)
        return True

    async def get(self, key: str) -> Optional[str]:
        """Simula GET de Redis"""
        if key in self._expiry and datetime.now() > self._expiry[key]:
            del self._data[key]
            del self._expiry[key]
            return None
        return self._data.get(key)

    async def delete(self, key: str) -> int:
        """Simula DELETE de Redis"""
        if key in self._data:
            del self._data[key]
            if key in self._expiry:
                del self._expiry[key]
            return 1
        return 0

    async def rpush(self, key: str, *values) -> int:
        """Simula RPUSH de Redis"""
        if key not in self._data:
            self._data[key] = []
        self._data[key].extend(values)
        return len(self._data[key])

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Simula LRANGE de Redis"""
        if key not in self._data:
            return []
        lst = self._data[key]
        if end == -1:
            return lst[start:]
        return lst[start:end+1]

    async def keys(self, pattern: str) -> List[str]:
        """Simula KEYS de Redis"""
        import re
        pattern_regex = pattern.replace('*', '.*')
        return [k for k in self._data.keys() if re.match(pattern_regex, k)]

    async def expire(self, key: str, seconds: int) -> bool:
        """Simula EXPIRE de Redis"""
        if key in self._data:
            self._expiry[key] = datetime.now() + timedelta(seconds=seconds)
            return True
        return False

    async def close(self):
        """Simula cierre de conexión"""
        pass


async def get_mock_redis():
    """Retorna una instancia de MockRedis"""
    return MockRedis()

