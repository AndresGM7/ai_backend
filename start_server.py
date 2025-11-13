"""
Script para iniciar el servidor de desarrollo
Sistema de Optimización de Precios
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("  🎯 Sistema de Optimización de Precios - Servidor de Desarrollo")
    print("=" * 70)
    print()
    print("  📍 API Base:     http://127.0.0.1:8000")
    print("  📚 Swagger Docs: http://127.0.0.1:8000/docs")
    print("  ✅ Status:       http://127.0.0.1:8000/status")
    print()
    print("  🚀 Características clave: API async, sesiones Redis, streaming, pricing & elasticidad")
    print("=" * 70)
    print()

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",  # Cambiar a 0.0.0.0 para permitir conexiones externas
        port=8000,
        reload=True,
        log_level="info",
        access_log=False,  # Deshabilitar logs de acceso para mejorar rendimiento
        workers=1  # Un solo worker en desarrollo
    )
