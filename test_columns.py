"""Test para verificar columnas generadas."""
import pandas as pd
from pathlib import Path

# Leer el CSV resultado
uploads_dir = Path(__file__).parent / "api" / "uploads"
csv_path = uploads_dir / "resultado.csv"

if csv_path.exists():
    df = pd.read_csv(csv_path, sep=';', decimal=',', nrows=0)
    print("=== COLUMNAS ACTUALES EN resultado.csv ===")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    print(f"\nTotal columnas: {len(df.columns)}")

    # Verificar columnas esperadas
    expected = [
        'recomendacion_precio',
        'rol_producto',
        'estrategia_recomendada',
        'precio_optimo_lineal',
        'demanda_optima_lineal',
        'revenue_optimo_lineal',
        'elasticidad_optima_lineal'
    ]

    print("\n=== VERIFICACIÓN DE COLUMNAS ESPERADAS ===")
    for col in expected:
        if col in df.columns:
            print(f"✓ {col} - PRESENTE")
        else:
            print(f"✗ {col} - FALTA")
else:
    print("El archivo resultado.csv no existe aún")

# Verificar imágenes generadas
print("\n=== IMÁGENES GENERADAS ===")
png_files = list(uploads_dir.glob("*.png"))
if png_files:
    for png in png_files:
        print(f"- {png.name} ({png.stat().st_size / 1024:.1f} KB)")
else:
    print("No se encontraron imágenes PNG")

