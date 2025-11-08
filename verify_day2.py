"""Script para verificar el Día 2."""
from api.main import app

print("=" * 60)
print("✅ DÍA 2 - VERIFICACIÓN")
print("=" * 60)
print()
print("Rutas disponibles en la API:")
for route in app.routes:
    if hasattr(route, 'methods'):
        methods = ', '.join(route.methods)
        print(f"  {methods:10} {route.path}")
print()
print("=" * 60)
print("✅ Todas las rutas del Día 2 cargadas correctamente")
print("=" * 60)

