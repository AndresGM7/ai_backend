"""Pricing routes: price optimization and elasticity endpoints."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import (
    PriceOptimizationRequest,
    PriceOptimizationResponse,
    ElasticityComputeRequest,
    ElasticityComputeResponse,
    CrossElasticityComputeRequest,
    CrossElasticityComputeResponse,
    DataUploadResponse,
)
from services.pricing_optimizer import optimize_price, calculate_elasticity, calculate_cross_elasticity

router = APIRouter()

# Simple in-memory store for uploaded data groups
DATA_STORE = {
    "raw_loaded": False,
    "groups": {},  # key -> list[(price, quantity)]
}


@router.post("/optimize-price", response_model=PriceOptimizationResponse)
async def optimize_price_endpoint(payload: PriceOptimizationRequest) -> PriceOptimizationResponse:
    try:
        p_star = optimize_price(
            current_price=payload.current_price,
            cost=payload.cost,
            elasticity=payload.elasticity,
            target_margin=payload.target_margin,
        )
        margin_pct = round(((p_star - payload.cost) / p_star) * 100.0, 2)
        delta_pct = ((p_star - payload.current_price) / payload.current_price) * 100.0
        action = "Sube" if delta_pct > 0 else ("Baja" if delta_pct < 0 else "Mantén")
        recommendation = f"{action} precio {abs(delta_pct):.2f}% para un margen de {margin_pct:.2f}%"

        estimated_demand = None
        estimated_revenue = None
        if payload.elasticity is not None and payload.demand_factor is not None:
            # Q = A * P^e
            estimated_demand = payload.demand_factor * (p_star ** payload.elasticity)
            estimated_revenue = p_star * estimated_demand

        return PriceOptimizationResponse(
            product_id=payload.product_id,
            optimal_price=round(p_star, 2),
            current_price=payload.current_price,
            estimated_demand=(round(estimated_demand, 4) if estimated_demand is not None else None),
            estimated_revenue=(round(estimated_revenue, 4) if estimated_revenue is not None else None),
            profit_margin=margin_pct,
            recommendation=recommendation,
            demand_factor=payload.demand_factor,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error optimizing price: {exc}")


@router.post("/elasticity/compute", response_model=ElasticityComputeResponse)
async def compute_elasticity(payload: ElasticityComputeRequest) -> ElasticityComputeResponse:
    try:
        obs_tuples = [(o.price, o.quantity) for o in payload.observations]
        result = calculate_elasticity(obs_tuples)
        return ElasticityComputeResponse(
            product_id=payload.product_id,
            elasticity=result["elasticity"],
            intercept=result.get("intercept", 0.0),
            demand_factor=result.get("demand_factor", 0.0),
            r2=result["r2"],
            n_points=result["n_points"],
            warnings=result["warnings"],
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error computing elasticity: {exc}")


@router.post("/elasticity/compute-cross", response_model=CrossElasticityComputeResponse)
async def compute_cross_elasticity(payload: CrossElasticityComputeRequest) -> CrossElasticityComputeResponse:
    try:
        triples = [(o.own_price, o.own_quantity, o.competitor_price) for o in payload.observations]
        result = calculate_cross_elasticity(triples)
        return CrossElasticityComputeResponse(
            product_id=payload.product_id,
            own_elasticity=result["own_elasticity"],
            cross_elasticity=result["cross_elasticity"],
            intercept=result["intercept"],
            r2=result["r2"],
            n_points=result["n_points"],
            warnings=result["warnings"],
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error computing cross elasticity: {exc}")


@router.post("/data/upload", response_model=DataUploadResponse)
async def upload_data(file: UploadFile = File(...)) -> DataUploadResponse:
    """Upload a CSV with columns from the Kaggle dataset and build groups for elasticity.

    Expected columns: invoice_no, customer_id, gender, age, category, quantity, price,
    payment_method, invoice_date, shopping_mall
    """
    try:
        import pandas as pd  # type: ignore
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"pandas not available: {exc}")

    try:
        content = await file.read()
        from io import BytesIO
        df = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}")

    required = {"invoice_no","customer_id","gender","age","category","quantity","price","payment_method","invoice_date","shopping_mall"}
    missing = required.difference(df.columns.astype(str).str.lower())
    # normalize columns to lower
    df.columns = [c.lower() for c in df.columns]

    missing = required.difference(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {sorted(list(missing))}")

    # Basic cleaning
    df = df.dropna(subset=["category","quantity","price"]).copy()
    # Coerce types
    for col in ("quantity","price","age"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["quantity","price"]).copy()
    df = df[(df["quantity"] > 0) & (df["price"] > 0)]

    # Group by category and keep (price, quantity) pairs
    groups = {}
    sample = []
    for cat, g in df.groupby("category"):
        pairs = list(zip(g["price"].astype(float).tolist(), g["quantity"].astype(float).tolist()))
        if len(pairs) >= 3:
            groups[str(cat)] = pairs
            if len(sample) < 5:
                sample.append({"category": str(cat), "observations": len(pairs)})

    DATA_STORE["raw_loaded"] = True
    DATA_STORE["groups"] = groups

    return DataUploadResponse(
        rows_loaded=int(len(df)),
        grouped_levels=int(len(groups)),
        group_sample=sample,
        warnings=[] if groups else ["No groups with >=3 observations found"]
    )
