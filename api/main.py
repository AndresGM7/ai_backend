"""FastAPI main application - Sistema de Optimización de Precios."""
import logging
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes import chat, stream
from models.schemas import StatusResponse


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


# ============================================
# Día 5: Middleware de medición de latencia
# ============================================

# Almacenamiento de métricas (en producción usar Prometheus)
latency_metrics = {
    "requests": [],
    "p50": 0,
    "p95": 0,
    "p99": 0,
    "avg": 0
}


@app.middleware("http")
async def measure_latency(request: Request, call_next):
    """
    Middleware para medir latencia de requests - Día 5.
    Calcula P50, P95, P99 y promedio.
    """
    start_time = time.perf_counter()

    # Procesar request
    response = await call_next(request)

    # Calcular latencia
    latency = (time.perf_counter() - start_time) * 1000  # en ms

    # Almacenar métrica
    latency_metrics["requests"].append(latency)

    # Mantener solo últimas 1000 requests
    if len(latency_metrics["requests"]) > 1000:
        latency_metrics["requests"] = latency_metrics["requests"][-1000:]

    # Calcular percentiles si tenemos suficientes datos
    if len(latency_metrics["requests"]) >= 10:
        sorted_latencies = sorted(latency_metrics["requests"])
        n = len(sorted_latencies)

        latency_metrics["p50"] = sorted_latencies[int(n * 0.50)]
        latency_metrics["p95"] = sorted_latencies[int(n * 0.95)]
        latency_metrics["p99"] = sorted_latencies[int(n * 0.99)]
        latency_metrics["avg"] = sum(sorted_latencies) / n

    # Agregar header con latencia
    response.headers["X-Process-Time"] = f"{latency:.2f}ms"

    # Log si la latencia es alta
    if latency > 200:
        logger.warning(f"High latency detected: {latency:.2f}ms for {request.url.path}")

    return response


# Incluir routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(stream.router, prefix="/api", tags=["Streaming"])


@app.get("/status", response_model=StatusResponse)
async def status():
    """Status endpoint con response model tipado - Día 4."""
    logger.info("status_check")
    return StatusResponse(
        status="ok",
        message="Server running asynchronously",
        project="Price Optimization System",
        week=1,
        features=["chat", "sessions", "streaming", "json-logging", "latency-tracking"]
    )


@app.get("/metrics")
async def get_metrics():
    """
    Endpoint de métricas - Día 5.
    Retorna latencias P50, P95, P99 y promedio.
    """
    return {
        "latency_ms": {
            "p50": round(latency_metrics["p50"], 2),
            "p95": round(latency_metrics["p95"], 2),
            "p99": round(latency_metrics["p99"], 2),
            "avg": round(latency_metrics["avg"], 2)
        },
        "total_requests": len(latency_metrics["requests"]),
        "status": "healthy" if latency_metrics["p95"] < 300 else "degraded"
    }
