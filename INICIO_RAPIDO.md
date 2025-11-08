# 🚀 Guía de Inicio Rápido - Sistema de Optimización de Precios

## 🎯 Proyecto: Semana 1 - Día 1

**Objetivo**: Configurar API profesional con FastAPI para sistema de optimización de precios basado en elasticidad.

## ✅ Estado Actual

Has completado la configuración inicial del proyecto con:
- ✅ FastAPI instalado y funcionando
- ✅ Endpoint `/status` implementado
- ✅ MockRedis para desarrollo (sin necesidad de Docker)
- ✅ OpenAI configurado
- ✅ Documentación Swagger automática

---

## 🎯 Cómo Iniciar el Servidor

### Opción 1: Script de Inicio (Recomendado)

```powershell
cd "C:\Users\Andres Giraldo\PycharmProjects\ai_backend"
poetry run python start_server.py
```

### Opción 2: Comando Uvicorn Directo

```powershell
cd "C:\Users\Andres Giraldo\PycharmProjects\ai_backend"
poetry run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Opción 3: Desde PyCharm (Mejor para desarrollo)

1. **Run > Edit Configurations > + > Python**

2. **Configuración:**
   - **Name**: `Start Price Optimizer`
   - **Script path**: `C:\Users\Andres Giraldo\PycharmProjects\ai_backend\start_server.py`
   - **Working directory**: `C:\Users\Andres Giraldo\PycharmProjects\ai_backend`
   - **Environment variables**: Carga desde `.env`

3. **Click ▶️ Run**

---

## 📊 Verificar que Funcione

### 1. Verifica el endpoint de status

Abre tu navegador o usa curl:

```bash
# Navegador
http://127.0.0.1:8000/status

# O con curl
curl http://127.0.0.1:8000/status
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "message": "Server running asynchronously",
  "project": "Price Optimization System"
}
```

### 2. Explora la documentación Swagger

Abre en tu navegador:
```
http://127.0.0.1:8000/docs
```

Aquí puedes:
- Ver todos los endpoints disponibles
- Probar los endpoints directamente
- Ver esquemas de request/response

---

## 📁 URLs Importantes

- **API Base**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Status Check**: http://127.0.0.1:8000/status

---

## 🎯 Día 1 - Checklist Completado

- [x] PyCharm configurado
- [x] Poetry + dependencias instaladas
- [x] FastAPI funcionando
- [x] Endpoint `/status` implementado
- [x] Swagger UI accesible
- [x] Logger configurado
- [x] README actualizado

---

## 📝 Próximos Pasos (Día 2)

Mañana implementarás:
1. Endpoint `/api/optimize-price` con validación Pydantic
2. Modelos de datos para precios y elasticidad
3. Lógica básica de cálculo de precio óptimo

---

## 🔧 Comandos Útiles

```powershell
# Verificar configuración completa
poetry run python check_setup.py

# Ejecutar tests
poetry run pytest

# Ver dependencias instaladas
poetry show

# Actualizar dependencias
poetry update
```

---

## 🆘 Troubleshooting

### Error: Puerto 8000 ocupado
```powershell
# Encuentra y mata el proceso
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Error: Module not found
```powershell
# Reinstalar dependencias
poetry install
```

### Error: OpenAI API Key inválida
Verifica tu `.env` y asegúrate que la API key sea válida y tenga créditos.

---

## 🎉 ¡Listo para Día 2!

Tu proyecto está configurado y funcionando. Puedes:
1. Commit tu progreso a Git
2. Documentar en tu portfolio
3. Prepararte para implementar la lógica de precios mañana

---

**Sistema de Optimización de Precios - Semana 1, Día 1 ✅**
