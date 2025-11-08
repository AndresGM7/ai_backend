# PyCharm Run Configuration Guide

## Configuración del Intérprete de Python

1. **File > Settings** (Ctrl+Alt+S)
2. **Project: ai_backend > Python Interpreter**
3. Click en el ícono de engranaje > **Add...**
4. Selecciona **Poetry Environment**
5. Poetry debe detectar automáticamente tu entorno

## Configuración de Run/Debug

### 1. Uvicorn Server (Desarrollo)

**Run > Edit Configurations > + > Python**

- **Name**: `Run API Server`
- **Script path**: Deja en blanco
- **Module**: `uvicorn`
- **Parameters**: `api.main:app --reload --host 127.0.0.1 --port 8000`
- **Working directory**: `C:\Users\Andres Giraldo\PycharmProjects\ai_backend`
- **Environment variables**: 
  - Click en el ícono de carpeta
  - Marca "Load from file"
  - Selecciona `.env`
  - O añade manualmente:
    ```
    OPENAI_API_KEY=tu_api_key
    REDIS_HOST=localhost
    REDIS_PORT=6379
    ```

### 2. Run Tests

**Run > Edit Configurations > + > Python tests > pytest**

- **Name**: `Run All Tests`
- **Target**: `Custom`
- **Test**: `tests/`
- **Working directory**: `C:\Users\Andres Giraldo\PycharmProjects\ai_backend`

### 3. Check Setup Script

**Run > Edit Configurations > + > Python**

- **Name**: `Check Setup`
- **Script path**: `C:\Users\Andres Giraldo\PycharmProjects\ai_backend\check_setup.py`

## Plugins Recomendados

Instala desde **File > Settings > Plugins**:

1. **EnvFile** - Para cargar archivos .env automáticamente
2. **Docker** - Para gestionar contenedores desde PyCharm
3. **Database Tools** (incluido) - Para conectarte a Redis

## Atajos de Teclado Útiles

- `Ctrl+Shift+F10` - Ejecutar el archivo actual
- `Shift+F10` - Ejecutar última configuración
- `Shift+F9` - Debug última configuración
- `Ctrl+Alt+R` - Seleccionar y ejecutar configuración

## Iniciar Redis

### Opción 1: Docker
```bash
docker run -d -p 6379:6379 --name redis-dev redis:7-alpine
```

### Opción 2: Docker Compose
```bash
cd docker
docker-compose up -d redis
```

### Opción 3: Windows Native (si tienes Redis instalado)
```bash
redis-server
```

## Verificar Instalación

Ejecuta en la terminal de PyCharm:

```bash
poetry run python check_setup.py
```

## Iniciar el Servidor de Desarrollo

```bash
poetry run uvicorn api.main:app --reload
```

O usa la configuración de Run que creaste arriba.

## Acceder a la API

- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/health

## Ejecutar Tests

```bash
# Todos los tests
poetry run pytest

# Con cobertura
poetry run pytest --cov=api --cov=services --cov=models

# Solo un archivo
poetry run pytest tests/test_status.py -v

# Solo tests async
poetry run pytest -k "async" -v
```
"""
Script de verificación rápida del proyecto
Ejecuta este script para verificar que todo esté configurado correctamente
"""
import sys


def check_imports():
    """Verifica que todas las dependencias estén disponibles"""
    print("🔍 Verificando dependencias...")
    
    try:
        import fastapi
        print("  ✓ FastAPI instalado")
    except ImportError:
        print("  ✗ FastAPI no encontrado")
        return False
    
    try:
        import redis
        print("  ✓ Redis instalado")
    except ImportError:
        print("  ✗ Redis no encontrado")
        return False
    
    try:
        import langchain
        print("  ✓ LangChain instalado")
    except ImportError:
        print("  ✗ LangChain no encontrado")
        return False
    
    try:
        import openai
        print("  ✓ OpenAI instalado")
    except ImportError:
        print("  ✗ OpenAI no encontrado")
        return False
    
    return True


def check_env():
    """Verifica las variables de entorno"""
    print("\n🔍 Verificando variables de entorno...")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    
    if openai_key and openai_key.startswith("sk-"):
        print("  ✓ OPENAI_API_KEY configurada")
    else:
        print("  ⚠ OPENAI_API_KEY no configurada o inválida")
    
    print(f"  ✓ REDIS_HOST: {redis_host}")
    print(f"  ✓ REDIS_PORT: {redis_port}")
    
    return True


def check_structure():
    """Verifica la estructura del proyecto"""
    print("\n🔍 Verificando estructura del proyecto...")
    
    import os
    
    required_dirs = [
        "api",
        "api/routes",
        "services",
        "models",
        "tests",
        "docker"
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory}")
        else:
            print(f"  ✗ {directory} no encontrado")
            all_exist = False
    
    return all_exist


def main():
    print("=" * 60)
    print("  🚀 AI Backend - Verificación de Configuración")
    print("=" * 60)
    
    checks = [
        check_imports(),
        check_env(),
        check_structure()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("  ✅ Proyecto configurado correctamente!")
        print("  Puedes ejecutar: poetry run uvicorn api.main:app --reload")
    else:
        print("  ⚠ Algunos problemas encontrados. Revisa arriba.")
    print("=" * 60)


if __name__ == "__main__":
    main()

