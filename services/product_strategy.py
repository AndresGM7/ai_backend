"""Product strategy classification and recommendation utilities.

Classifies products into strategic roles based on elasticity and volume,
and provides pricing and strategic recommendations.
"""
from typing import Optional, Tuple


def price_recommendation(elasticity_abs: Optional[float]) -> str:
    """Generate price recommendation based on elasticity magnitude.

    Args:
        elasticity_abs: Absolute value of price elasticity

    Returns:
        Price recommendation: "Subir mucho", "Subir", "Mantener", "Bajar", "Bajar mucho"

    Classification:
        - |e| > 2: Muy elástico -> "Bajar mucho"
        - 1 <= |e| <= 2: Elástico -> "Bajar"
        - 0.5 < |e| < 1: Moderadamente inelástico -> "Mantener"
        - 0.2 <= |e| <= 0.5: Inelástico -> "Subir"
        - |e| < 0.2: Muy inelástico -> "Subir mucho"
    """
    if elasticity_abs is None:
        return "Mantener"

    if elasticity_abs > 2.0:
        return "Bajar mucho"
    elif elasticity_abs >= 1.0:
        return "Bajar"
    elif elasticity_abs > 0.5:
        return "Mantener"
    elif elasticity_abs >= 0.2:
        return "Subir"
    else:
        return "Subir mucho"


def classify_product_role(elasticity_abs: Optional[float], volume_rel: Optional[float]) -> str:
    """Classify product role based on absolute elasticity and relative volume.

    Args:
        elasticity_abs: Absolute value of elasticity (relative to category)
        volume_rel: Relative volume (product volume / category average volume)

    Returns:
        Product role: "Generador de ganancias", "Estabilizador de ingresos",
                     "Generador de trafico", "Promesa de valor", "Sin clasificar"

    Matrix:
        - Generador de ganancias (Vacas): Inelástica (|e| < 1) & Alto volumen (> 1)
        - Estabilizador de ingresos (Perros): Inelástica (|e| < 1) & Bajo volumen (<= 1)
        - Generador de trafico (Estrellas): Elástica (|e| >= 1) & Alto volumen (> 1)
        - Promesa de valor (Apalancamiento): Elástica (|e| >= 1) & Bajo volumen (<= 1)
    """
    if elasticity_abs is None or volume_rel is None:
        return "Sin clasificar"

    is_elastic = elasticity_abs >= 1.0
    is_high_vol = volume_rel > 1.0

    if (not is_elastic) and is_high_vol:
        return "Generador de ganancias"
    elif (not is_elastic) and (not is_high_vol):
        return "Estabilizador de ingresos"
    elif is_elastic and is_high_vol:
        return "Generador de trafico"
    else:  # elastic and low vol
        return "Promesa de valor"


def strategic_recommendation(role: str) -> str:
    """Generate detailed strategic recommendation based on product role.

    Args:
        role: Product role classification

    Returns:
        Detailed strategic recommendation text
    """
    strategies = {
        "Generador de ganancias": (
            "Maximizar márgenes: Subir precios gradualmente sin perder volumen. "
            "Producto con demanda inelástica y alto volumen. "
            "Priorizar disponibilidad, calidad y mantener cuota de mercado. "
            "Fuente estable de ingresos y efectivo."
        ),
        "Estabilizador de ingresos": (
            "Posicionamiento premium: Mantener precios altos para nicho leal. "
            "Demanda inelástica con bajo volumen. "
            "Enfocarse en calidad superior, exclusividad y segmentación de clientes de alto valor. "
            "Considerar descontinuar si los márgenes no justifican el inventario."
        ),
        "Generador de trafico": (
            "Estrategia de penetración: Precios competitivos y promociones agresivas. "
            "Alta sensibilidad al precio con alto volumen. "
            "Priorizar adquisición de clientes, cross-selling y ventas complementarias. "
            "Ofrecer descuentos estratégicos para aumentar volumen y cuota de mercado."
        ),
        "Promesa de valor": (
            "Posicionamiento por valor: Precio competitivo con diferenciación por calidad. "
            "Producto sensible al precio con bajo volumen. "
            "Invertir en marketing, branding y fidelización para aumentar volumen. "
            "Reducir precios para penetrar mercado y convertir en 'Generador de trafico'."
        ),
        "Sin clasificar": (
            "Recopilar más datos históricos de precios y ventas para realizar "
            "análisis de elasticidad y volumen. Se requieren al menos 3 observaciones "
            "de precio-cantidad para estimar elasticidad confiable."
        )
    }
    return strategies.get(role, "Mantener estrategia actual y monitorear comportamiento de demanda.")


def analyze_product(
    elasticity_rel: Optional[float],
    volume_rel: Optional[float]
) -> Tuple[str, str, str]:
    """Perform complete product analysis: price recommendation, role, and strategy.

    Args:
        elasticity_rel: Relative elasticity (product elasticity / category elasticity)
        volume_rel: Relative volume (product volume / category average volume)

    Returns:
        Tuple of (price_recommendation, role, strategy)
    """
    try:
        # Calculate absolute elasticity for classification
        elasticity_abs = abs(float(elasticity_rel)) if elasticity_rel is not None else None

        # Generate recommendations
        price_rec = price_recommendation(elasticity_abs)
        role = classify_product_role(elasticity_abs, volume_rel)
        strategy = strategic_recommendation(role)

        return price_rec, role, strategy

    except Exception:
        return "Mantener", "Sin clasificar", strategic_recommendation("Sin clasificar")
