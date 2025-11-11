# AI Backend – Price Optimization System

Backend en FastAPI para análisis y optimización de precios usando elasticidad, sesiones en Redis, streaming y pruebas automatizadas. Incluye cálculo de elasticidad propia y cruzada, recomendación de precio óptimo y carga de datos CSV para generar series de precio-cantidad por categoría.

## Características clave
- FastAPI async + Pydantic (validación y tipado)
- Redis (session management; MockRedis fallback)
- Endpoints de streaming (texto y SSE JSON)
- Cálculo de elasticidad (log-log) e intercepto (factor de demanda A)
- Elasticidad cruzada (precio propio vs competidor)
- Recomendación de precio óptimo con soporte de demanda estimada
- Carga de CSV para agrupar datos y preparar observaciones
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
- POST /api/data/upload – Carga CSV y genera grupos por categoría

## Flujo de optimización
1. Subir datos vía /api/data/upload (CSV con columnas: invoice_no, customer_id, gender, age, category, quantity, price, payment_method, invoice_date, shopping_mall).
2. Calcular elasticidad para una categoría con /api/elasticity/compute proporcionando observaciones (precio, cantidad).
3. Usar respuesta (elasticity, demand_factor) para alimentar /api/optimize-price y obtener precio óptimo + demanda estimada.
4. Futuro: combinar con LLM para explicación avanzada y escenarios, cachear en Redis y exponer endpoint premium.

## Quick start
```bash
git clone https://github.com/AndresGM7/ai_backend.git
cd ai_backend
poetry install
poetry run python start_server.py
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

## Carga de CSV
Formato recomendado para evitar problemas con locales que usan coma como separador decimal:
- Separe columnas con punto y coma (;)
- Use coma (,) como separador decimal en números (ej: 1.234,56 -> 1234.56 en notación local)

Archivo ejemplo (sample.csv) — formato con punto y coma como separador:
```csv
invoice_no;customer_id;gender;age;category;quantity;price;payment_method;invoice_date;shopping_mall
I000001;C000001;M;34;Electronics;5;100;cash;2025-01-01;MallA
I000002;C000002;F;29;Electronics;4;120;credit;2025-01-02;MallA
I000003;C000003;M;41;Electronics;3;140;debit;2025-01-03;MallA
I000004;C000004;F;37;Clothing;2;60;cash;2025-01-01;MallB
I000005;C000005;M;33;Clothing;3;55;credit;2025-01-02;MallB
I000006;C000006;F;26;Clothing;4;50;debit;2025-01-03;MallB
```
Subir (ejemplo usando curl):
```bash
curl -X POST http://127.0.0.1:8000/api/data/upload -F "file=@sample.csv"
```
Notas:
- El servidor detectará automáticamente CSVs separados por comas o por punto y coma, y soporta números con coma decimal. Para evitar ambigüedades recomendamos usar punto y coma como separador y coma para decimales.
- El archivo resultado generado por el servidor (uploads/resultado.csv) estará en formato punto y coma con coma como separador decimal para que abra correctamente en hojas de cálculo configuradas en ese locale.

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
poetry run pytest --cov=api --cov=services --cov-report=term-missing
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
