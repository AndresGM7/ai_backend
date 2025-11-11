import math
from fastapi.testclient import TestClient
from api.main import app
from services.pricing_optimizer import estimate_linear_demand, optimal_price_from_linear

client = TestClient(app)


def test_estimate_linear_demand_manual():
    # Use known linear demand Q = 100 - 2P
    observations = [(10.0, 80.0), (20.0, 60.0), (30.0, 40.0), (40.0, 20.0)]
    res = estimate_linear_demand(observations)
    assert res["n_points"] == 4
    assert math.isclose(res["alpha"], 100.0, rel_tol=1e-3)
    assert math.isclose(res["beta"], -2.0, rel_tol=1e-3)
    assert 0.9 <= res["r2"] <= 1.0


def test_optimal_price_from_linear_function():
    alpha = 100.0
    beta = -2.0
    res = optimal_price_from_linear(alpha, beta)
    assert res.get("valid") is True
    assert math.isclose(res.get("p_star"), 25.0, rel_tol=1e-6)


def test_optimize_price_linear_endpoint_with_observations():
    payload = {
        "product_id": "TEST-LIN-001",
        "current_price": 20.0,
        "observations": [
            {"price": 10.0, "quantity": 80.0},
            {"price": 20.0, "quantity": 60.0},
            {"price": 30.0, "quantity": 40.0},
            {"price": 40.0, "quantity": 20.0}
        ]
    }
    resp = client.post("/api/optimize-price-linear", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # optimal price should be approx 25
    assert data["optimal_price"] == round(25.0, 2)
    assert data["product_id"] == payload["product_id"]
    assert "precio" in data["recommendation"].lower() or "maximizar" in data["recommendation"].lower()

