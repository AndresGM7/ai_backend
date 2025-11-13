"""Pydantic models for request/response validation."""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Modelos base con validación
# ============================================

class ChatRequest(BaseModel):
    """Request model para chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "¿Cuál es el precio óptimo para mi producto?"
            }
        }
    )


class ChatResponse(BaseModel):
    """Response model para chat endpoint."""
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
    demand_factor: Optional[float] = Field(None, gt=0, description="Factor A de demanda (Q = A * P^e) para estimar demanda y revenue")

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
    demand_factor: Optional[float] = Field(None, description="Factor A usado para estimar demanda")

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
# Modelos de Elasticidad
# ============================================

class PriceQuantity(BaseModel):
    price: float = Field(..., gt=0, description="Precio unitario")
    quantity: float = Field(..., gt=0, description="Cantidad vendida")


class ElasticityComputeRequest(BaseModel):
    product_id: Optional[str] = Field(None, description="ID del producto o categoría")
    observations: List[PriceQuantity] = Field(..., min_length=3, description="Lista de observaciones (precio, cantidad)")


class ElasticityComputeResponse(BaseModel):
    product_id: Optional[str]
    elasticity: float
    intercept: float
    demand_factor: float
    r2: float
    n_points: int
    warnings: List[str] = []


# ============================================
# Cross Elasticity Models
# ============================================
class CrossElasticityObservation(BaseModel):
    own_price: float = Field(..., gt=0)
    own_quantity: float = Field(..., gt=0)
    competitor_price: float = Field(..., gt=0)


class CrossElasticityComputeRequest(BaseModel):
    product_id: Optional[str] = None
    observations: List[CrossElasticityObservation] = Field(..., min_length=4)


class CrossElasticityComputeResponse(BaseModel):
    product_id: Optional[str]
    own_elasticity: float
    cross_elasticity: float
    intercept: float
    r2: float
    n_points: int
    warnings: List[str] = []

# ============================================
# Data upload
# ============================================
class GroupSampleItem(BaseModel):
    category: str = Field(..., description="Nombre del grupo (categoría o default)")
    observations: int = Field(..., ge=0, description="Número de observaciones válidas")


class GroupElasticityItem(BaseModel):
    """Detailed group item including elasticity estimates."""
    category: str = Field(..., description="Nombre del grupo (categoría or default)")
    observations: int = Field(..., ge=0, description="Número de observaciones válidas")
    elasticity: Optional[float] = Field(None, description="Estimated own-price elasticity (slope)")
    intercept: Optional[float] = Field(None, description="Regression intercept on log-log scale")
    demand_factor: Optional[float] = Field(None, description="Demand factor A in Q = A * P^e")
    r2: float = Field(..., description="R^2 of the log-log regression")
    n_points: int = Field(..., description="Number of points used in regression")
    warnings: List[str] = Field(default_factory=list, description="Warnings from estimation")


class DataUploadResponse(BaseModel):
    rows_loaded: int
    grouped_levels: int
    # Provide detailed elasticity per group (if any)
    group_sample: List[GroupElasticityItem]
    warnings: List[str] = []
    # URL to download processed CSV with per-product elasticity/price columns (if generated)
    download_url: Optional[str] = None
    # URLs for generated images (if available)
    image_urls: List[str] = []
    # URLs for generated report CSVs (if available)
    report_urls: List[str] = []


# ============================================
# Modelos de Sistema
# ============================================

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    redis: str
    service: str


class StatusResponse(BaseModel):
    """Response mejorado para endpoint status."""
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


class LinearOptimizationRequest(BaseModel):
    """Request to compute revenue-maximizing price for a linear demand model.

    Provide either alpha and beta directly (alpha + beta * P) or a list of observations
    to estimate them.
    """
    product_id: Optional[str] = None
    current_price: float = Field(..., gt=0)
    alpha: Optional[float] = Field(None, description="Intercept of linear demand Q = alpha + beta*P")
    beta: Optional[float] = Field(None, description="Slope (dQ/dP) of linear demand")
    observations: Optional[List[PriceQuantity]] = Field(None, description="Optional observations to estimate linear demand (price, quantity)")


class LinearOptimizationResponse(BaseModel):
    product_id: Optional[str]
    optimal_price: Optional[float]
    current_price: float
    estimated_demand: Optional[float]
    estimated_revenue: Optional[float]
    elasticity_at_optimal: Optional[float]
    recommendation: str
    warnings: List[str] = []
