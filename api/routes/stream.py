"""Streaming endpoints - Día 3."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger("ai_backend")


async def _stream_text(text: str):
    """Generator para streaming de texto palabra por palabra."""
    for chunk in text.split():
        yield chunk + " "
        await asyncio.sleep(0.15)


@router.get("/stream")
async def stream():
    """
    Endpoint de streaming demo usando Server-Sent Events.

    Día 3: Demuestra capacidad de streaming para respuestas largas.
    Útil para integración con LLMs que responden token por token.

    Returns:
        StreamingResponse con texto palabra por palabra
    """
    logger.info("Streaming endpoint called")
    return StreamingResponse(
        _stream_text("Hola Andrés, streaming works! Sistema de optimización de precios funcionando correctamente."),
        media_type="text/plain"
    )


@router.get("/stream-json")
async def stream_json():
    """
    Streaming de eventos JSON (SSE - Server-Sent Events).

    Útil para enviar múltiples actualizaciones al cliente en tiempo real.
    """
    import json

    async def generate():
        events = [
            {"event": "start", "data": "Iniciando análisis de precios"},
            {"event": "progress", "data": "Calculando elasticidad... 33%"},
            {"event": "progress", "data": "Analizando con IA... 66%"},
            {"event": "progress", "data": "Generando recomendación... 100%"},
            {"event": "complete", "data": "Precio óptimo: $98.50"}
        ]

        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.5)

    logger.info("JSON streaming endpoint called")
    return StreamingResponse(generate(), media_type="text/event-stream")

