"""FastAPI main application - Sistema de Optimización de Precios."""
import logging
from fastapi import FastAPI

# Logger básico (JSON logs más adelante)
logger = logging.getLogger("ai_backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="AI Backend - Sistema de Optimización de Precios",
    description="API para optimización de precios basada en elasticidad con IA",
    version="0.1.0"
)


@app.get("/status")
async def status():
    """Status endpoint - verifica que el servidor esté funcionando."""
    logger.info("status_check")
    return {
        "status": "ok",
        "message": "Server running asynchronously",
        "project": "Price Optimization System"
    }
