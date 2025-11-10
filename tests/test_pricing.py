import math
from fastapi.testclient import TestClient
from api.main import app
from services.pricing_optimizer import optimize_price

client = TestClient(app)


def test_optimize_price_margin_fallback():
    # Sin elasticidad usa regla de margen
    cost = 50.0
    target_margin = 0.4
    expected = cost / (1 - target_margin)
    result = optimize_price(current_price=55.0, cost=cost, elasticity=None, target_margin=target_margin)
    assert math.isclose(result, expected, rel_tol=1e-3)


def test_optimize_price_elasticity():
    # Elasticidad negativa (< -1) usa fórmula p* = c * e / (e + 1)
    cost = 60.0
    elasticity = -1.5
    expected = cost * (elasticity / (elasticity + 1))  # 60 * (-1.5 / -0.5) = 180
    result = optimize_price(current_price=100.0, cost=cost, elasticity=elasticity, target_margin=0.3)
    assert math.isclose(result, expected, rel_tol=1e-3)


def test_optimize_price_endpoint_elasticity():
    payload = {
        "product_id": "PROD-XYZ",
        "current_price": 120.0,
        "cost": 60.0,
        "elasticity": -1.5,
        "target_margin": 0.3
    }
    resp = client.post("/api/optimize-price", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Optimal price should match elasticity formula (rounded 2 decimals)
    expected = 60.0 * (-1.5 / (-1.5 + 1))  # 180
    assert data["optimal_price"] == round(expected, 2)
    assert data["product_id"] == payload["product_id"]
    assert "margen" in data["recommendation"].lower() or "precio" in data["recommendation"].lower()


def test_optimize_price_endpoint_margin_fallback():
    payload = {
        "product_id": "PROD-NO-ELASTIC",
        "current_price": 70.0,
        "cost": 50.0,
        "target_margin": 0.4
    }
    resp = client.post("/api/optimize-price", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    expected = 50.0 / (1 - 0.4)
    assert data["optimal_price"] == round(expected, 2)

