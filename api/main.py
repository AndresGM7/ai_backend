"""FastAPI main application - Sistema de Optimización de Precios."""
import logging
import json
from fastapi import FastAPI

from api.routes import chat, stream


# ============================================
# JSON Logging para mejor observabilidad
# ============================================
class JsonFormatter(logging.Formatter):
    """Formateador de logs en JSON para mejor observabilidad."""

    def format(self, record):
        payload = {
            "time": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Agregar exception info si existe
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


# Configurar logging con JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger("ai_backend")
logger.handlers = [handler]
logger.setLevel(logging.INFO)

app = FastAPI(
    title="AI Backend - Sistema de Optimización de Precios",
    description="API para optimización de precios basada en elasticidad con IA",
    version="0.1.0"
)

# Incluir routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(stream.router, prefix="/api", tags=["Streaming"])


@app.get("/status")
async def status():
    """Status endpoint - verifica que el servidor esté funcionando."""
    logger.info("status_check")
    return {
        "status": "ok",
        "message": "Server running asynchronously",
        "project": "Price Optimization System",
        "week": 1,
        "features": ["chat", "sessions", "streaming", "json-logging"]
    }
