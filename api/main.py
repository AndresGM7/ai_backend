"""FastAPI main application - Price Optimization System."""
import logging
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes import chat, stream, pricing
from models.schemas import StatusResponse


# ============================================
# JSON logging for observability
# ============================================
class JsonFormatter(logging.Formatter):
    """JSON log formatter for better observability."""

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

        # Add exception info if present
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


# Configure logging with JSON formatter
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
# Request latency middleware
# ============================================

# In-memory metrics (for production, prefer Prometheus)
latency_metrics = {
    "requests": [],
    "p50": 0,
    "p95": 0,
    "p99": 0,
    "avg": 0
}


@app.middleware("http")
async def measure_latency(request: Request, call_next):
    """Middleware that measures request latency and computes basic stats."""
    start_time = time.perf_counter()

    # Process request
    response = await call_next(request)

    # Calculate latency
    latency = (time.perf_counter() - start_time) * 1000  # in ms

    # Store metric
    latency_metrics["requests"].append(latency)

    # Keep only latest 1000 requests
    if len(latency_metrics["requests"]) > 1000:
        latency_metrics["requests"] = latency_metrics["requests"][-1000:]

    # Calculate percentiles if we have enough data
    if len(latency_metrics["requests"]) >= 10:
        sorted_latencies = sorted(latency_metrics["requests"])
        n = len(sorted_latencies)

        latency_metrics["p50"] = sorted_latencies[int(n * 0.50)]
        latency_metrics["p95"] = sorted_latencies[int(n * 0.95)]
        latency_metrics["p99"] = sorted_latencies[int(n * 0.99)]
        latency_metrics["avg"] = sum(sorted_latencies) / n

    # Add header with latency
    response.headers["X-Process-Time"] = f"{latency:.2f}ms"

    # Log if latency is high
    if latency > 200:
        logger.warning(f"High latency detected: {latency:.2f}ms for {request.url.path}")

    return response


# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(stream.router, prefix="/api", tags=["Streaming"])
app.include_router(pricing.router, prefix="/api", tags=["Pricing"])


@app.get("/")
async def root():
    """Root endpoint with quick links."""
    return {
        "message": "AI Backend running",
        "docs": "/docs",
        "status": "/status",
        "api": "/api"
    }


@app.get("/status", response_model=StatusResponse)
async def status():
    """Typed status endpoint."""
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
    """Return latency percentiles and basic health info."""
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
