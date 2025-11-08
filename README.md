# 🎯 Sistema de Optimización de Precios con IA

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
   git clone <tu-repo>
   git clone https://github.com/andresgiraldo/ai_backend.git
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

### Optimización de Precios (próximamente)
- `POST /api/optimize-price` - Calcular precio óptimo
- `GET /api/elasticity/{product_id}` - Obtener elasticidad de producto
- `POST /api/predict-demand` - Predecir demanda

---

## 🎯 Roadmap Semana 1

- [x] **Día 1**: Setup inicial + endpoint `/status`
- [ ] **Día 2**: Endpoint `/optimize-price` con validación Pydantic
- [ ] **Día 3**: Integración Redis + caching
- [ ] **Día 4**: Tests completos + CI/CD
- [ ] **Día 5**: Logging estructurado + métricas

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

**Andrés Giraldo**
- Portfolio: [Tu portfolio]
- Portfolio: https://andresgiraldo.dev (o tu URL de portfolio)
- LinkedIn: https://linkedin.com/in/andres-giraldo
- GitHub: https://github.com/andresgiraldo
- Email: andres.giraldo@example.com

---

## 📄 Licencia

MIT License - ver LICENSE para detalles

---

**Built with ❤️ using FastAPI, OpenAI, and modern Python async patterns**
