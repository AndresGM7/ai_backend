"""Pricing optimizer utilities: elasticity model and price recommendation.

Implements:
- Constant-elasticity optimal price formula
- Margin fallback pricing
- Elasticity estimation via log-log regression (own-price)
- Cross elasticity via multivariate log-log regression
"""
from typing import Optional, List, Tuple, Dict
import math

try:
    from sklearn.linear_model import LinearRegression
except ImportError:  # scikit-learn may not be installed yet in some environments
    LinearRegression = None  # type: ignore


def optimize_price(
    current_price: float,
    cost: float,
    elasticity: Optional[float] = None,
    target_margin: Optional[float] = 0.3,
) -> float:
    """Compute an optimal price.

    If elasticity is provided (< -1 assumed), use constant-elasticity profit optimum:
        p* = c * e / (e + 1)   with e < -1
    Else fall back to target margin formula:
        p* = c / (1 - m)
    """
    if elasticity is not None:
        e = elasticity
        # Guard rails
        if e >= -0.1:
            # Elasticity too close to 0 -> fallback to margin rule
            pass
        else:
            denom = e + 1.0
            # Avoid division by zero near e = -1
            if abs(denom) > 1e-6:
                p_star = cost * (e / denom)
                # Ensure price not below cost
                return max(p_star, cost * 1.01)
    # Margin fallback
    m = target_margin if target_margin is not None else 0.3
    m = min(max(m, 0.0), 0.95)
    return max(cost / (1.0 - m), cost * 1.01)


def calculate_elasticity(price_quantity: List[Tuple[float, float]]) -> Dict[str, object]:
    """Estimate own-price elasticity using log-log regression.

    price_quantity: list of (price, quantity) observations.

    Returns dict with:
      elasticity: slope of ln(Q) vs ln(P)
      intercept: intercept of ln(Q) = a + b ln(P)
      demand_factor: A = exp(intercept) so Q = A * P^e
      r2: coefficient of determination
      n_points: number of valid points
      warnings: list of warning strings

    Filters invalid (price <=0, quantity <=0) observations, returns warnings if <3 points.
    """
    warnings: List[str] = []
    cleaned: List[Tuple[float, float]] = [
        (p, q) for p, q in price_quantity if p > 0 and q > 0
    ]
    n_points = len(cleaned)
    if n_points < 3:
        return {
            "elasticity": float("nan"),
            "intercept": float("nan"),
            "demand_factor": float("nan"),
            "r2": 0.0,
            "n_points": n_points,
            "warnings": ["Insufficient data points (need >=3)"]
        }

    # Log transform
    log_p = [math.log(p) for p, _ in cleaned]
    log_q = [math.log(q) for _, q in cleaned]

    # If sklearn not available fallback to manual slope calc
    if LinearRegression is None:
        # Simple ordinary least squares slope for y= a + b x
        mean_x = sum(log_p) / n_points
        mean_y = sum(log_q) / n_points
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_p, log_q))
        den = sum((x - mean_x) ** 2 for x in log_p)
        if den == 0:
            warnings.append("No price variance; elasticity undefined")
            return {
                "elasticity": float("nan"),
                "intercept": float("nan"),
                "demand_factor": float("nan"),
                "r2": 0.0,
                "n_points": n_points,
                "warnings": warnings
            }
        slope = num / den
        # R2 manual
        ss_tot = sum((y - mean_y) ** 2 for y in log_q)
        ss_res = sum((y - (mean_y + slope * (x - mean_x))) ** 2 for x, y in zip(log_p, log_q))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        intercept = mean_y - slope * mean_x
        demand_factor = math.exp(intercept)
        return {
            "elasticity": slope,
            "intercept": intercept,
            "demand_factor": demand_factor,
            "r2": r2,
            "n_points": n_points,
            "warnings": warnings
        }

    # Use LinearRegression
    X = [[x] for x in log_p]
    y = log_q
    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]
    r2 = model.score(X, y)
    intercept = model.intercept_
    demand_factor = math.exp(intercept)

    if abs(slope) < 1e-3:
        warnings.append("Elasticity near zero; demand appears inelastic")
    if r2 < 0.3:
        warnings.append("Low R2; elasticity estimate may be unreliable")

    return {
        "elasticity": slope,
        "intercept": intercept,
        "demand_factor": demand_factor,
        "r2": r2,
        "n_points": n_points,
        "warnings": warnings
    }


def calculate_cross_elasticity(
    triples: List[Tuple[float, float, float]]
) -> Dict[str, object]:
    """Estimate own and cross price elasticities using multivariate log-log regression.

    triples: list of (own_price, own_quantity, competitor_price)
    Returns dict with own_elasticity (b1), cross_elasticity (b2), intercept, r2, n_points, warnings.
    """
    warnings: List[str] = []
    cleaned = [(pi, qi, pj) for (pi, qi, pj) in triples if pi > 0 and qi > 0 and pj > 0]
    n = len(cleaned)
    if n < 4:
        return {
            "own_elasticity": float("nan"),
            "cross_elasticity": float("nan"),
            "intercept": float("nan"),
            "r2": 0.0,
            "n_points": n,
            "warnings": ["Insufficient data points (need >=4)"]
        }

    log_pi = [math.log(pi) for (pi, _, __) in cleaned]
    log_qi = [math.log(qi) for (_, qi, __) in cleaned]
    log_pj = [math.log(pj) for (*__, pj) in cleaned]

    if LinearRegression is None:
        warnings.append("scikit-learn not available; cross elasticity requires sklearn")
        return {
            "own_elasticity": float("nan"),
            "cross_elasticity": float("nan"),
            "intercept": float("nan"),
            "r2": 0.0,
            "n_points": n,
            "warnings": warnings
        }

    import numpy as np

    X = np.column_stack([log_pi, log_pj])
    y = log_qi
    model = LinearRegression()
    model.fit(X, y)
    b1, b2 = model.coef_.tolist()
    intercept = model.intercept_
    r2 = model.score(X, y)

    return {
        "own_elasticity": b1,
        "cross_elasticity": b2,
        "intercept": intercept,
        "r2": r2,
        "n_points": n,
        "warnings": warnings
    }


def estimate_linear_demand(price_quantity: List[Tuple[float, float]]) -> Dict[str, object]:
    """Estimate linear demand Q = alpha + beta * P using OLS.

    Returns dict with:
      alpha: intercept
      beta: slope (dQ/dP)
      r2: coefficient of determination
      n_points: number of valid points
      warnings: list of warning strings

    Filters invalid (price <=0, quantity < 0) observations. Requires >=3 points for stability.
    """
    warnings: List[str] = []
    cleaned: List[Tuple[float, float]] = [
        (p, q) for p, q in price_quantity if p > 0 and q >= 0
    ]
    n_points = len(cleaned)
    if n_points < 3:
        return {
            "alpha": float("nan"),
            "beta": float("nan"),
            "r2": 0.0,
            "n_points": n_points,
            "warnings": ["Insufficient data points (need >=3)"]
        }

    # Prepare X and y
    X_vals = [p for p, _ in cleaned]
    y_vals = [q for _, q in cleaned]

    # If sklearn not available, do manual OLS for y = alpha + beta * x
    if LinearRegression is None:
        mean_x = sum(X_vals) / n_points
        mean_y = sum(y_vals) / n_points
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(X_vals, y_vals))
        den = sum((x - mean_x) ** 2 for x in X_vals)
        if den == 0:
            warnings.append("No price variance; linear demand undefined")
            return {
                "alpha": float("nan"),
                "beta": float("nan"),
                "r2": 0.0,
                "n_points": n_points,
                "warnings": warnings
            }
        beta = num / den
        alpha = mean_y - beta * mean_x
        # R2 manual
        ss_tot = sum((y - mean_y) ** 2 for y in y_vals)
        ss_res = sum((y - (alpha + beta * x)) ** 2 for x, y in zip(X_vals, y_vals))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        return {
            "alpha": alpha,
            "beta": beta,
            "r2": r2,
            "n_points": n_points,
            "warnings": warnings
        }

    # Use sklearn LinearRegression
    X = [[x] for x in X_vals]
    y = y_vals
    model = LinearRegression()
    model.fit(X, y)
    beta = float(model.coef_[0])
    alpha = float(model.intercept_)
    r2 = float(model.score(X, y))

    if abs(beta) < 1e-6:
        warnings.append("Slope near zero; demand appears flat")
    if r2 < 0.3:
        warnings.append("Low R2; linear demand estimate may be unreliable")

    return {
        "alpha": alpha,
        "beta": beta,
        "r2": r2,
        "n_points": n_points,
        "warnings": warnings
    }


def optimal_price_from_linear(alpha: float, beta: float) -> Dict[str, object]:
    """Compute revenue-maximizing price for linear demand Q = alpha + beta*P.

    Analytical optimum: P* = -alpha / (2 * beta)  (requires beta < 0 and P* > 0)
    Returns dict with p_star (float or nan), valid (bool), warning messages if any.
    """
    warnings: List[str] = []
    try:
        if beta >= 0:
            warnings.append("Beta >= 0 (non-negative slope): linear demand does not decline with price")
            return {"p_star": float("nan"), "valid": False, "warnings": warnings}
        denom = 2.0 * beta
        if abs(denom) < 1e-12:
            warnings.append("Beta too small; division unstable")
            return {"p_star": float("nan"), "valid": False, "warnings": warnings}
        p_star = -alpha / denom
        if p_star <= 0:
            warnings.append("Computed optimal price not positive")
            return {"p_star": float("nan"), "valid": False, "warnings": warnings}
        return {"p_star": float(p_star), "valid": True, "warnings": warnings}
    except Exception as exc:
        warnings.append(f"Error computing optimal price: {exc}")
        return {"p_star": float("nan"), "valid": False, "warnings": warnings}


__all__ = [
    "optimize_price",
    "calculate_elasticity",
    "calculate_cross_elasticity",
    "estimate_linear_demand",
    "optimal_price_from_linear",
]
