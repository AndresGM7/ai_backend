# 🎯 Sistema de Optimización de Precios con IA

[![CI Pipeline](https://github.com/AndresGM7/ai_backend/workflows/CI%20Pipeline/badge.svg)](https://github.com/AndresGM7/ai_backend/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Sistema inteligente de optimización de precios** basado en elasticidad de demanda, análisis predictivo con LLMs y backend asíncrono en FastAPI.

---

## 📋 Stack Tecnológico

- **Backend**: FastAPI (Python async)
- **IA/ML**: OpenAI GPT-4, LangChain
- **Cache**: Redis (con MockRedis para desarrollo)
- **Testing**: pytest, pytest-asyncio
- **Deployment**: Docker, Docker Compose

---

## 🚀 Cómo Ejecutar Localmente

### Prerrequisitos

- Python 3.12+
- Poetry (gestor de dependencias)
- OpenAI API Key

### Instalación

1. **Clonar el repositorio**
   ```bash
   ```

   ```

2. **Instalar dependencias**
   ```bash
   poetry install
   poetry shell
   ```

3. **Configurar variables de entorno**
   
   El archivo `.env` ya está configurado. Asegúrate de tener tu `OPENAI_API_KEY` válida.

4. **Iniciar el servidor**
   ```bash
   poetry run python start_server.py
   ```
   
   O directamente:
   ```bash
   poetry run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Verificar que funciona**
   - API: http://127.0.0.1:8000
   - Documentación Swagger: http://127.0.0.1:8000/docs
   - Status: http://127.0.0.1:8000/status

---

## 📁 Estructura del Proyecto

```
ai_backend/
├── api/
│   ├── main.py              # FastAPI app + endpoints
│   ├── deps.py              # Dependency injection
│   └── routes/              # Módulos de rutas
├── services/
│   ├── pricing_optimizer.py # Lógica de optimización
│   ├── llm_service.py       # Integración con LLMs
│   ├── redis_manager.py     # Gestión de cache
│   └── mock_redis.py        # Redis simulado
├── models/
│   └── schemas.py           # Modelos Pydantic
├── tests/
│   └── test_*.py            # Tests unitarios
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env                     # Variables de entorno
├── pyproject.toml           # Dependencias Poetry
└── README.md
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
poetry run pytest

# Con cobertura
poetry run pytest --cov=api --cov=services

# Tests específicos
poetry run pytest tests/test_pricing.py -v
```

---

## 📊 Endpoints Disponibles

### Status
- `GET /status` - Verificar estado del servidor

### Chat & Session Management (Día 2)
- `POST /api/chat/{user_id}` - Enviar mensaje y guardar en sesión
- `GET /api/chat/{user_id}/history` - Obtener historial de conversación
- `DELETE /api/chat/{user_id}/history` - Limpiar historial de usuario

### Streaming (Día 3) 🆕
- `GET /api/stream` - Demo de streaming texto
- `GET /api/stream-json` - Streaming de eventos JSON (SSE)

### Optimización de Precios (próximamente)
- `POST /api/optimize-price` - Calcular precio óptimo
- `GET /api/elasticity/{product_id}` - Obtener elasticidad de producto
- `POST /api/predict-demand` - Predecir demanda

---

## 💾 Session Management con Redis

### Arquitectura de Sesiones

El sistema implementa gestión de sesiones con Redis para mantener el contexto de conversación:

**Características:**
- ✅ **Persistencia**: Historial de mensajes por usuario
- ✅ **TTL Automático**: Sesiones expiran en 1 hora (3600 segundos)
- ✅ **Almacenamiento JSON**: Datos serializados para flexibilidad
- ✅ **Fallback a MockRedis**: Funciona sin Docker

**Estructura de Sesión:**
```json
{
  "history": [
    {
      "role": "user",
      "text": "¿Cuál es el precio óptimo?"
    }
  ]
}
```

**Seguridad:**
- Session keys por `user_id`
- TTL para limpieza automática
- Sin datos sensibles en sesión
- Aislamiento por usuario

**Ejemplo de uso:**
```bash
# Enviar mensaje
curl -X POST "http://localhost:8000/api/chat/user123" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, necesito ayuda con precios"}'

# Obtener historial
curl "http://localhost:8000/api/chat/user123/history"
```

---

## 🎯 Roadmap Semana 1

- [x] **Día 1**: Setup inicial + endpoint `/status`
- [x] **Día 2**: Redis sessions + endpoint `/chat/{user_id}`
- [x] **Día 3**: Streaming + Logging JSON + Tests completos
- [ ] **Día 4**: Validación Pydantic avanzada + OpenAPI mejorado
- [ ] **Día 5**: Performance monitoring + Benchmarks

---

## 💡 Features Clave

- ✅ **API Asíncrona** - Alto rendimiento con FastAPI
- ✅ **IA Integrada** - OpenAI GPT-4 para análisis
- ✅ **Cache Inteligente** - Redis para optimización
- ✅ **Tests Completos** - Cobertura >80%
- ✅ **Docker Ready** - Despliegue simplificado
- ✅ **Documentación Auto** - Swagger UI integrado

---

## 📝 Notas de Desarrollo

### Semana 1 - Backend Asíncrono
Objetivo: API profesional, testeada y versionada para portfolio

**Día 1 (Actual)**: 
- ✅ PyCharm configurado
- ✅ Endpoint `/status` funcionando
- ✅ Swagger UI activo
- ✅ Git inicializado

---

## 👨‍💻 Autor
- Portfolio: https://andresgm7.github.io (GitHub Pages)
- Portfolio: [Tu portfolio]
- GitHub: https://github.com/AndresGM7
- Email: andresgiraldo1988@gmail.com
- GitHub: https://github.com/andresgiraldo
- Email: andres.giraldo@example.com

---

## 📄 Licencia

MIT License - ver LICENSE para detalles

---

**Built with ❤️ using FastAPI, OpenAI, and modern Python async patterns**
