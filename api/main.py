"""FastAPI main application - Sistema de Optimización de Precios."""
import logging
from fastapi import FastAPI

from api.routes import chat

# Logger básico (JSON logs más adelante)
logger = logging.getLogger("ai_backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="AI Backend - Sistema de Optimización de Precios",
    description="API para optimización de precios basada en elasticidad con IA",
    version="0.1.0"
)

# Incluir router de chat
app.include_router(chat.router, prefix="/api", tags=["Chat"])


@app.get("/status")
async def status():
    """Status endpoint - verifica que el servidor esté funcionando."""
    logger.info("status_check")
    return {
        "status": "ok",
        "message": "Server running asynchronously",
        "project": "Price Optimization System",
        "day": "2 - Redis Session Management"
    }
