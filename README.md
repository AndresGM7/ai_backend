# AI Backend – Price Optimization System

Backend en FastAPI para análisis y optimización de precios usando elasticidad, sesiones en Redis, streaming y pruebas automatizadas.

Nota: Esta rama pública omite las funcionalidades de carga y descarga de datos (endpoints de upload/download) por motivos comerciales.

## Características clave
- FastAPI async + Pydantic (validación y tipado)
- Redis (session management; MockRedis fallback)
- Endpoints de streaming (texto y SSE JSON)
- Cálculo de elasticidad (log-log) e intercepto (factor de demanda A)
- Elasticidad cruzada (precio propio vs competidor)
- Recomendación de precio óptimo con soporte de demanda estimada
- Métricas de latencia (p50, p95, p99, promedio) y header de tiempo
- Logging estructurado JSON
- Suite de tests (pytest) y modelos Pydantic documentados

## Endpoints
- GET  /status – Estado del servicio
- GET  /metrics – Métricas de latencia
- POST /api/chat/{user_id} – Guarda mensaje en sesión
- GET  /api/chat/{user_id}/history – Historial de conversación
- DELETE /api/chat/{user_id}/history – Limpia historial
- GET  /api/stream – Streaming de texto
- GET  /api/stream-json – Streaming SSE JSON
- POST /api/optimize-price – Precio óptimo (usa margen o elasticidad)
- POST /api/elasticity/compute – Elasticidad propia + intercepto + factor demanda
- POST /api/elasticity/compute-cross – Elasticidad propia y cruzada (competidor)

## Flujo de optimización
1. Calcular elasticidad para una categoría con /api/elasticity/compute proporcionando observaciones (precio, cantidad).
2. Usar respuesta (elasticity, demand_factor) para alimentar /api/optimize-price y obtener precio óptimo + demanda estimada.

## Quick start
```bash
poetry install
poetry run uvicorn api.main:app --reload
# Docs: http://127.0.0.1:8000/docs
```

## Ejemplo: Elasticidad propia
```bash
curl -X POST http://127.0.0.1:8000/api/elasticity/compute \
  -H "Content-Type: application/json" \
  -d '{"product_id":"electronics","observations":[{"price":100,"quantity":500},{"price":120,"quantity":450},{"price":140,"quantity":400}]}'
```
Respuesta (ejemplo):
```json
{
  "product_id": "electronics",
  "elasticity": -0.85,
  "intercept": 7.12,
  "demand_factor": 1234.5,
  "r2": 0.78,
  "n_points": 3,
  "warnings": []
}
```

## Ejemplo: Precio óptimo con demanda
```bash
curl -X POST http://127.0.0.1:8000/api/optimize-price \
  -H "Content-Type: application/json" \
  -d '{"product_id":"electronics","current_price":120,"cost":70,"elasticity":-1.2,"demand_factor":1500}'
```
Respuesta (ejemplo):
```json
{
  "product_id": "electronics",
  "optimal_price": 140.0,
  "current_price": 120.0,
  "estimated_demand": 310.22,
  "estimated_revenue": 43430.8,
  "profit_margin": 50.0,
  "recommendation": "Sube precio 16.67% para un margen de 50.00%",
  "demand_factor": 1500.0
}
```

## Sesiones en Redis
- Historial por usuario (clave = user_id)
- TTL auto: 3600s
- Fallback a MockRedis si Redis no está disponible

## Testing
```bash
poetry run pytest -q
```
Agrega cobertura:
```bash
poetry run pytest --cov=api --cov=services --cov=models --cov-report=term-missing
```

## Próximo potencial (extensiones)
- Integración LLM: análisis narrativo + clasificación de sensibilidad
- Cache LLM + invalidación por contexto
- Batch elasticity por categoría con datos cargados
- Prometheus + Grafana para métricas formales
- Autenticación y cuotas (free vs premium)

## Mantenimiento
- Código modular (api/routes, services, models)
- Logging estructurado para integrarse con herramientas de observabilidad
- Métricas simples listas para evolucionar a Prometheus

## Autor
Andrés Giraldo (@AndresGM7) – andresgiraldo1988@gmail.com

Licencia: MIT
