"""Pydantic models for request/response validation - Día 4."""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Día 4: Modelos base con validación
# ============================================

class ChatRequest(BaseModel):
    """Request model para chat endpoint - Día 4."""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "¿Cuál es el precio óptimo para mi producto?"
            }
        }
    )


class ChatResponse(BaseModel):
    """Response model para chat endpoint - Día 4."""
    response: str = Field(..., description="Respuesta del sistema")
    session_len: int = Field(..., ge=0, description="Longitud del historial de sesión")
    user_id: str = Field(..., description="ID del usuario")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Mensaje guardado correctamente",
                "session_len": 5,
                "user_id": "user123"
            }
        }
    )


class Message(BaseModel):
    """Individual message in conversation history."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")


class ChatHistoryResponse(BaseModel):
    """Response model for conversation history."""
    user_id: str = Field(..., description="Session identifier")
    messages: List[Message] = Field(..., description="Conversation messages")
    message_count: int = Field(..., description="Total message count")


# ============================================
# Modelos para Optimización de Precios
# ============================================

class PriceOptimizationRequest(BaseModel):
    """Request para optimización de precios."""
    product_id: str = Field(..., description="ID del producto")
    current_price: float = Field(..., gt=0, description="Precio actual")
    cost: float = Field(..., gt=0, description="Costo del producto")
    elasticity: Optional[float] = Field(None, lt=0, description="Elasticidad de precio (negativa)")
    target_margin: Optional[float] = Field(0.3, ge=0, le=1, description="Margen objetivo (0-1)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "PROD-001",
                "current_price": 100.00,
                "cost": 60.00,
                "elasticity": -1.5,
                "target_margin": 0.35
            }
        }
    )


class PriceOptimizationResponse(BaseModel):
    """Response con precio optimizado."""
    product_id: str
    optimal_price: float = Field(..., description="Precio óptimo calculado")
    current_price: float
    estimated_demand: Optional[float] = Field(None, description="Demanda estimada")
    estimated_revenue: Optional[float] = Field(None, description="Revenue estimado")
    profit_margin: float = Field(..., description="Margen de ganancia (%)")
    recommendation: str = Field(..., description="Recomendación en lenguaje natural")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "PROD-001",
                "optimal_price": 98.50,
                "current_price": 100.00,
                "estimated_demand": 525,
                "estimated_revenue": 51712.50,
                "profit_margin": 39.09,
                "recommendation": "Bajar precio 1.5% aumentará revenue 3.4%"
            }
        }
    )


# ============================================
# Modelos de Sistema
# ============================================

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    redis: str
    service: str


class StatusResponse(BaseModel):
    """Response mejorado para endpoint status - Día 4."""
    status: str
    message: str
    project: str
    week: int
    features: List[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "message": "Server running asynchronously",
                "project": "Price Optimization System",
                "week": 1,
                "features": ["chat", "sessions", "streaming", "json-logging"]
            }
        }
    )
