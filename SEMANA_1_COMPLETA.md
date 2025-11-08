# Específico
poetry run pytest tests/test_chat.py::test_chat_endpoint_creates_session

# Con prints
poetry run pytest -s

# Coverage
poetry run pytest --cov --cov-report=term-missing
```

### Git

```bash
# Ver estado
git status

# Commits
git log --oneline --graph

# Crear rama para feature
git checkout -b feature/pricing-optimizer

# Subir cambios
git push origin main
```

### Docker

```bash
# Construir imagen
docker build -f docker/Dockerfile -t ai_backend:latest .

# Ver imágenes
docker images

# Ver contenedores activos
docker ps

# Logs de contenedor
docker logs ai_backend_api
```

---

## 📸 Screenshots para Portfolio

### Capturas Esenciales:

1. ✅ **Swagger UI completo** (`/docs`)
2. ✅ **Respuesta de /status**
3. ✅ **POST /chat con session_len creciendo**
4. ✅ **GET /history mostrando persistencia**
5. ✅ **Streaming en acción** (GIF)
6. ✅ **Tests pasando** (pytest -v)
7. ✅ **Coverage report** (>80%)
8. ✅ **Docker Compose logs**

---

## 🎯 Próximos Pasos - Semana 2

### Implementación de Optimización de Precios

1. **CSV Upload & Parsing**
```python
@router.post("/api/upload-data")
async def upload_pricing_data(file: UploadFile):
    # Parse CSV
    # Validar datos
    # Calcular elasticidad
    pass
```

2. **Cálculo de Elasticidad**
```python
def calculate_elasticity(historical_data: List[PricePoint]) -> float:
    # Regresión lineal log-log
    # Q = a * P^e
    pass
```

3. **Integración con LLM**
```python
async def analyze_with_llm(data: PricingData) -> PricingRecommendation:
    # Prompt engineering
    # OpenAI GPT-4 analysis
    # Structured output
    pass
```

4. **Dashboard Frontend** (Opcional)
   - Streamlit o React
   - Visualización de elasticidad
   - Gráficos de revenue projection

---

## 💡 Consejos para Recruiters

### Puntos Clave a Mencionar

1. **Arquitectura**
   - API REST asíncrona con FastAPI
   - Separación de concerns (api/services/models)
   - Dependency injection

2. **Session Management**
   - Persistencia con Redis
   - TTL para limpieza automática
   - Aislamiento por usuario

3. **Validación & Type Safety**
   - Pydantic models
   - OpenAPI auto-generado
   - Type hints completo

4. **Testing**
   - pytest con >80% coverage
   - Tests async
   - Mocking de dependencias

5. **DevOps**
   - Docker & Docker Compose
   - CI/CD con GitHub Actions
   - Environment variables

6. **Performance**
   - Streaming responses
   - Logging estructurado
   - Métricas de latencia

---

## 🎓 Conceptos Técnicos Implementados

- ✅ **Async/Await**: Programación asíncrona en Python
- ✅ **REST API**: Endpoints RESTful
- ✅ **Session Management**: Estado distribuido con Redis
- ✅ **Dependency Injection**: FastAPI deps pattern
- ✅ **Testing**: Unit & integration tests
- ✅ **Streaming**: Server-Sent Events (SSE)
- ✅ **Logging**: Structured logging (JSON)
- ✅ **Validation**: Pydantic data validation
- ✅ **Containerization**: Docker multi-stage
- ✅ **Documentation**: OpenAPI/Swagger

---

## 💼 Monetización - Estrategias

### 1. SaaS (Software as a Service)
```
Freemium Model:
- Free: 100 optimizaciones/mes
- Pro ($49/mes): 1000 optimizaciones
- Enterprise ($299/mes): Ilimitado + soporte
```

### 2. API Marketplace
- RapidAPI
- AWS Marketplace
- Azure Marketplace

### 3. Consultoría
- Implementación custom
- Integración con ERP
- Training y soporte

### 4. White Label
- Vender la tecnología a empresas
- Customización por industria

---

## 🔗 Links Importantes

- **Repositorio:** https://github.com/AndresGM7/ai_backend
- **Documentación:** http://localhost:8000/docs (local)
- **LinkedIn:** https://linkedin.com/in/andres-giraldo
- **Portfolio:** https://andresgm7.github.io

---

## 📝 Changelog

### v0.1.0 - Semana 1 (2024-11-08)

**Added:**
- FastAPI setup completo
- Redis session management
- Chat endpoints con persistencia
- Streaming responses
- JSON structured logging
- Tests con pytest (>80% coverage)
- Docker & Docker Compose
- CI/CD pipeline básico

**Features:**
- Session TTL automático
- MockRedis fallback
- Pydantic validation
- OpenAPI documentation
- Performance metrics

---

## 🎉 ¡Semana 1 Completada!

Has construido una API profesional con:
- ✅ 6+ endpoints funcionando
- ✅ Session management con Redis
- ✅ Tests implementados
- ✅ Docker ready
- ✅ Documentación completa

**Siguiente:** Implementar la lógica de optimización de precios con elasticidad en Semana 2.

---

**Autor:** Andrés Giraldo  
**GitHub:** @AndresGM7  
**Email:** andresgiraldo1988@gmail.com  
**Status:** ✅ Listo para Portfolio & Recruiters

---

**Built with ❤️ using FastAPI, Redis, OpenAI & modern Python patterns**
# 🎯 SEMANA 1 COMPLETA - Sistema de Optimización de Precios con IA

## 📅 Resumen Ejecutivo

**Proyecto:** Sistema de Optimización de Precios basado en Elasticidad  
**Stack:** FastAPI, Redis, OpenAI, LangChain, Docker  
**Objetivo:** API profesional para calcular precios óptimos usando análisis de elasticidad y IA  
**Status:** ✅ Semana 1 Completada

---

## ✅ Logros de la Semana 1

### Día 1: Setup + Endpoint Base
- ✅ PyCharm configurado con Poetry
- ✅ FastAPI funcionando
- ✅ Endpoint `GET /status`
- ✅ Swagger UI operativo
- ✅ Git inicializado

### Día 2: Redis Session Management
- ✅ `services/redis_manager.py` con save/get session
- ✅ Endpoint `POST /api/chat/{user_id}` - Guardar mensajes
- ✅ Endpoint `GET /api/chat/{user_id}/history` - Ver historial
- ✅ Endpoint `DELETE /api/chat/{user_id}/history` - Limpiar sesión
- ✅ TTL de 1 hora por sesión
- ✅ MockRedis para desarrollo sin Docker

### Día 3: Streaming + Logging JSON + Tests
- ✅ Endpoint streaming con SSE
- ✅ Logging estructurado en JSON
- ✅ Tests con pytest y pytest-asyncio
- ✅ Test coverage configurado

### Día 4: Validación Pydantic + OpenAPI
- ✅ Modelos Pydantic para request/response
- ✅ Documentación automática mejorada
- ✅ Type safety completo

### Día 5: Performance Monitoring
- ✅ Middleware de medición de latencia
- ✅ Métricas P50/P95/P99
- ✅ Benchmarks documentados

---

## 🏗️ Arquitectura del Sistema

### Flujo de Optimización de Precios

```
Usuario carga CSV → API procesa datos → 
  ↓
Cálculo de Elasticidad → LLM analiza contexto →
  ↓
Recomendación de Precio Óptimo → Cache en Redis →
  ↓
Respuesta JSON + Métricas
```

### Componentes Principales

1. **API Layer** (`api/`)
   - FastAPI endpoints
   - Validación con Pydantic
   - Streaming responses

2. **Service Layer** (`services/`)
   - `pricing_optimizer.py` - Lógica de elasticidad
   - `redis_manager.py` - Session management
   - `llm_service.py` - Integración OpenAI

3. **Data Layer**
   - Redis para sesiones y cache
   - CSV parsing para datos de usuario

---

## 📊 Endpoints Implementados

### Status & Health
```
GET /status
```
Verifica estado del servidor

### Chat & Sessions
```
POST   /api/chat/{user_id}           - Enviar mensaje
GET    /api/chat/{user_id}/history   - Ver historial
DELETE /api/chat/{user_id}/history   - Limpiar sesión
```

### Streaming
```
GET /api/stream
```
Demo de streaming con Server-Sent Events

### Optimización de Precios (Próximo)
```
POST /api/optimize-price
  Body: {
    "product_id": "PROD-001",
    "current_price": 100.00,
    "cost": 60.00,
    "historical_data": [...],
    "elasticity": -1.5
  }
```

---

## 🧪 Testing & Quality

### Ejecutar Tests

```bash
# Todos los tests
poetry run pytest

# Con cobertura
poetry run pytest --cov=api --cov=services --cov-report=html

# Solo tests específicos
poetry run pytest tests/test_chat.py -v

# Ver reporte de cobertura
open htmlcov/index.html  # En Windows: start htmlcov/index.html
```

### Tests Implementados

- ✅ `test_status.py` - Endpoint de status
- ✅ `test_chat.py` - Session management
- ✅ `test_stream.py` - Streaming endpoints
- ✅ Cobertura > 80%

---

## 🚀 Cómo Ejecutar el Proyecto

### Opción 1: Desarrollo Local (Recomendado para empezar)

```bash
# 1. Clonar e instalar
git clone https://github.com/AndresGM7/ai_backend.git
cd ai_backend
poetry install

# 2. Configurar .env (ya incluido)
# OPENAI_API_KEY ya está configurada

# 3. Iniciar servidor
poetry run python start_server.py

# 4. Abrir Swagger UI
# http://127.0.0.1:8000/docs
```

### Opción 2: Con Docker Compose

```bash
# Construir y ejecutar
cd docker
docker-compose up --build

# En segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

### Opción 3: Solo Redis en Docker

```bash
# Iniciar Redis
docker run -d -p 6379:6379 --name redis-dev redis:7-alpine

# Iniciar API local
poetry run python start_server.py
```

---

## 📈 Optimización de Precios - Concepto de Elasticidad

### ¿Qué es la Elasticidad de Precio?

La elasticidad mide cómo cambia la demanda cuando cambias el precio:

```
Elasticidad = % Cambio en Cantidad / % Cambio en Precio
```

**Ejemplo:**
- Si elasticidad = -2.0: al subir precio 10%, demanda baja 20%
- Si elasticidad = -0.5: al subir precio 10%, demanda baja 5%

### Flujo de Trabajo del Usuario

1. **Cargar CSV con datos históricos:**
```csv
fecha,precio,cantidad_vendida,costo_unitario
2024-01-01,100,500,60
2024-01-02,95,550,60
2024-01-03,105,480,60
```

2. **API calcula elasticidad automáticamente**

3. **LLM analiza:**
   - Tendencias de mercado
   - Competencia
   - Estacionalidad
   - Costos

4. **Retorna precio óptimo:**
```json
{
  "optimal_price": 98.50,
  "estimated_demand": 525,
  "estimated_revenue": 51712.50,
  "profit_margin": 39.09,
  "elasticity": -1.8,
  "confidence": 0.87,
  "recommendation": "Bajar precio 1.5% aumentará revenue 3.4%"
}
```

---

## 💾 Session Management Detallado

### Arquitectura de Sesiones

**Storage:** Redis con TTL de 1 hora

**Estructura:**
```json
{
  "user_id": "user123",
  "history": [
    {"role": "user", "text": "Mensaje 1"},
    {"role": "assistant", "text": "Respuesta 1"}
  ],
  "metadata": {
    "created_at": "2024-11-08T10:00:00",
    "last_activity": "2024-11-08T10:05:00"
  }
}
```

**Características:**
- ✅ Aislamiento por usuario
- ✅ TTL automático (limpieza)
- ✅ Fallback a MockRedis
- ✅ Sin datos sensibles

---

## 🔧 Comandos Útiles

### Desarrollo

```bash
# Verificar setup
poetry run python check_setup.py

# Iniciar servidor con reload
poetry run uvicorn api.main:app --reload

# Ver dependencias
poetry show

# Actualizar dependencias
poetry update
```

### Testing

```bash
# Tests básicos
poetry run pytest

# Verbose
poetry run pytest -v


