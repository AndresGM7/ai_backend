"""Pricing routes: price optimization and elasticity endpoints."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from datetime import datetime

from models.schemas import (
    PriceOptimizationRequest,
    PriceOptimizationResponse,
    ElasticityComputeRequest,
    ElasticityComputeResponse,
    CrossElasticityComputeRequest,
    CrossElasticityComputeResponse,
    DataUploadResponse,
    LinearOptimizationRequest,
    LinearOptimizationResponse,
)
from services.pricing_optimizer import optimize_price, calculate_elasticity, calculate_cross_elasticity, estimate_linear_demand, optimal_price_from_linear
from services.product_strategy import analyze_product
from services.report_generator import generate_pricing_report

router = APIRouter()

# Simple in-memory store for uploaded data groups
DATA_STORE: Dict[str, Any] = {
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
        recommendation = f"{action} precio {abs(round(delta_pct, 2)):.2f}% para un margen de {margin_pct:.2f}%"

        estimated_demand = None
        estimated_revenue = None
        if payload.elasticity is not None and payload.demand_factor is not None:
            # Q = A * P^e
            estimated_demand = payload.demand_factor * (p_star ** payload.elasticity)
            estimated_revenue = p_star * estimated_demand

        return PriceOptimizationResponse(
            product_id=payload.product_id,
            optimal_price=round(p_star, 2),
            current_price=round(payload.current_price, 2),
            estimated_demand=(round(estimated_demand, 2) if estimated_demand is not None else None),
            estimated_revenue=(round(estimated_revenue, 2) if estimated_revenue is not None else None),
            profit_margin=margin_pct,
            recommendation=recommendation,
            demand_factor=(round(payload.demand_factor, 2) if payload.demand_factor is not None else None),
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
            elasticity=round(float(result["elasticity"]), 2) if result["elasticity"] == result["elasticity"] else float("nan"),
            intercept=round(float(result.get("intercept", 0.0)), 2),
            demand_factor=round(float(result.get("demand_factor", 0.0)), 2),
            r2=round(float(result["r2"]), 2),
            n_points=int(result["n_points"]),
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
            own_elasticity=round(float(result["own_elasticity"]), 2) if result["own_elasticity"] == result["own_elasticity"] else float("nan"),
            cross_elasticity=round(float(result["cross_elasticity"]), 2) if result["cross_elasticity"] == result["cross_elasticity"] else float("nan"),
            intercept=round(float(result["intercept"]), 2) if result["intercept"] == result["intercept"] else float("nan"),
            r2=round(float(result["r2"]), 2),
            n_points=int(result["n_points"]),
            warnings=result["warnings"],
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error computing cross elasticity: {exc}")


@router.post("/data/upload", response_model=DataUploadResponse)
async def upload_data(file: UploadFile = File(...)) -> DataUploadResponse:
    """Upload a CSV and produce enriched resultado.csv with product and category elasticities and relative metrics.

    Robust behavior:
    - product elasticity requires >=3 observations; otherwise fallback to category elasticity if available
    - missing elasticities reported as 'N/A'
    - volumes missing reported as 0; relative ratios use 'N/A' when division not possible
    """
    try:
        import pandas as pd  # local import
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"pandas not available: {exc}")

    try:
        content = await file.read()
        from io import BytesIO
        # Try several parsing strategies to handle locales where decimals are written with a comma
        parse_attempts = []
        # 1) Default pandas sniffing
        parse_attempts.append({'sep': None, 'decimal': '.' , 'thousands': None})
        # 2) Semicolon separator and comma decimals (common in many locales)
        parse_attempts.append({'sep': ';', 'decimal': ',', 'thousands': '.'})
        # 3) Comma decimal with default separator
        parse_attempts.append({'sep': None, 'decimal': ',', 'thousands': '.'})
        # 4) Semicolon + comma decimal without thousands
        parse_attempts.append({'sep': ';', 'decimal': ',', 'thousands': None})

        def try_parse(opt):
            try:
                if opt['sep'] is None:
                    return pd.read_csv(BytesIO(content), decimal=opt['decimal'], thousands=opt['thousands'])
                else:
                    return pd.read_csv(BytesIO(content), sep=opt['sep'], decimal=opt['decimal'], thousands=opt['thousands'])
            except Exception:
                return None

        best_df = None
        best_valid = -1
        for opt in parse_attempts:
            df_try = try_parse(opt)
            if df_try is None:
                continue
            # normalize column names temporarily for heuristics
            df_try.columns = [str(c).strip().lower().replace(' ', '_').replace('-', '_') for c in df_try.columns]
            # quick heuristic: if price/quantity columns exist, count valid numeric rows
            # We don't yet know which columns are price/qty (matching happens later) but try to find likely candidates
            possible_qty = [c for c in df_try.columns if any(k in c for k in ['qty', 'quantity', 'sold', 'units', 'cantidad', 'cant'])]
            possible_price = [c for c in df_try.columns if any(k in c for k in ['price', 'precio', 'prc', 'unit_price'])]
            if not possible_qty or not possible_price:
                # fallback: consider any numeric-like columns
                numeric_counts = df_try.apply(lambda s: pd.to_numeric(s, errors='coerce').notna().sum())
                valid_rows = int(numeric_counts.max()) if not numeric_counts.empty else 0
            else:
                qcol = possible_qty[0]
                pcol = possible_price[0]
                qn = pd.to_numeric(df_try[qcol], errors='coerce')
                pn = pd.to_numeric(df_try[pcol], errors='coerce')
                valid_rows = int(((qn.notna()) & (pn.notna())).sum())

            if valid_rows > best_valid:
                best_valid = valid_rows
                best_df = df_try

        if best_df is None:
            raise HTTPException(status_code=400, detail="Invalid CSV: could not parse with expected formats")

        df = best_df
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}")

    # Normalize column names
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

    def find_col(possible: List[str]) -> Optional[str]:
        for cand in possible:
            if cand in df.columns:
                return cand
        return None

    price_syn = ["price", "unit_price", "unitprice", "precio", "prc"]
    cost_syn = ["cost", "unit_cost", "costo", "cost_price", "unitcost"]
    qty_syn = ["quantity", "qty", "quantities", "sold", "quantity_sold", "cantidad", "units", "qty_sold", "total_quantity", "cant", "cantidades"]
    cat_syn = ["category", "categoria", "product_category", "dept", "department", "segment", "group", "familia"]
    # product/name synonyms — include common SKU/id variants
    name_syn = ["name", "product", "product_name", "item", "item_name", "sku", "descripcion", "description", "sku_id", "skuid", "sku-id", "product_id", "productid", "product-id", "id", "item_id", "itemid"]
    date_syn = ["invoice_date", "date", "fecha", "order_date", "transaction_date", "datetime", "ts", "created_at", "timestamp"]

    price_col = find_col(price_syn)
    cost_col = find_col(cost_syn)
    qty_col = find_col(qty_syn)
    cat_col = find_col(cat_syn)
    name_col = find_col(name_syn)
    date_col = find_col(date_syn)

    # If no explicit product/name column matched, try simple heuristics (contains 'sku' or 'product'+'id')
    if name_col is None:
        for col in df.columns:
            if "sku" in col:
                name_col = col
                break
        if name_col is None:
            for col in df.columns:
                if "product" in col and "id" in col:
                    name_col = col
                    break

    missing_minimal = [k for k, v in {"price": price_col, "quantity": qty_col}.items() if v is None]
    if missing_minimal:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_minimal} (accepts synonyms)")

    # Coerce numeric and filter positive
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce")
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[qty_col, price_col]).copy()
    df = df[(df[qty_col] > 0) & (df[price_col] > 0)]

    # Normalize text identifier columns to avoid split groups due to whitespace/case differences
    if name_col and name_col in df.columns:
        df[name_col] = df[name_col].astype(str).str.strip()
    if cat_col and cat_col in df.columns:
        df[cat_col] = df[cat_col].astype(str).str.strip()

    # For grouping behavior, ensure we treat grouping key values as cleaned strings
    # Determine grouping key
    group_key = cat_col or name_col

    # Build mapping of all category/name pairs (for averages) and separate groups used for elasticity (>=3 obs)
    all_category_pairs: Dict[str, List[tuple]] = {}
    if group_key:
        for key, g in df.groupby(group_key):
            k = str(key).strip()
            pairs = list(zip(g[price_col].astype(float).tolist(), g[qty_col].astype(float).tolist()))
            all_category_pairs[k] = pairs
    else:
        pairs = list(zip(df[price_col].astype(float).tolist(), df[qty_col].astype(float).tolist()))
        all_category_pairs["default"] = pairs

    # Groups eligible for elasticity estimation (require >=3 points)
    groups: Dict[str, List[tuple]] = {k: v for k, v in all_category_pairs.items() if len(v) >= 3}

    DATA_STORE["raw_loaded"] = True
    DATA_STORE["groups"] = groups

    # Category-level elasticity and avg volumes (compute avg for ALL categories, elasticity only when enough points)
    category_stats: Dict[str, Dict[str, Any]] = {}
    for cat, pairs in all_category_pairs.items():
        res = calculate_elasticity(pairs) if len(pairs) >= 3 else {}
        cat_el = res.get("elasticity") if res and res.get("elasticity") == res.get("elasticity") else None
        intercept = res.get("intercept") if res and res.get("intercept") == res.get("intercept") else None
        demand_factor = res.get("demand_factor") if res and res.get("demand_factor") == res.get("demand_factor") else None
        r2 = float(res.get("r2", 0.0)) if res else 0.0
        n_points = int(res.get("n_points", len(pairs))) if res else len(pairs)
        # avg volume per category (computed for all categories)
        try:
            mask = df[group_key] == cat if group_key else slice(None)
            cat_avg_vol = float(df.loc[mask, qty_col].astype(float).mean())
            if cat_avg_vol != cat_avg_vol:  # NaN guard
                cat_avg_vol = 0.0
        except Exception:
            cat_avg_vol = 0.0
        warnings_cat = res.get("warnings", []) if res else (["Insufficient data points (need >=3)"] if len(pairs) < 3 else [])
        # Linear demand estimation for category (alpha + beta * P)
        lin = estimate_linear_demand(pairs) if len(pairs) >= 3 else {}
        lin_alpha = lin.get("alpha") if lin and lin.get("alpha") == lin.get("alpha") else None
        lin_beta = lin.get("beta") if lin and lin.get("beta") == lin.get("beta") else None
        lin_p_star = None
        lin_est_demand = None
        lin_rev = None
        lin_warnings = lin.get("warnings", []) if lin else []
        if lin_alpha is not None and lin_beta is not None:
            opt_lin = optimal_price_from_linear(lin_alpha, lin_beta)
            lin_warnings.extend(opt_lin.get("warnings", []))
            if opt_lin.get("valid"):
                lin_p_star = float(opt_lin.get("p_star"))
                lin_est_demand = lin_alpha + lin_beta * lin_p_star
                if lin_est_demand is not None and lin_est_demand < 0:
                    lin_warnings.append("Estimated demand at linear optimal price is negative; clipped to 0")
                    lin_est_demand = 0.0
                lin_rev = (lin_p_star * lin_est_demand) if lin_est_demand is not None else None

        category_stats[cat] = {
            "elasticity": cat_el,
            "intercept": intercept,
            "demand_factor": demand_factor,
            "r2": r2,
            "n_points": n_points,
            "avg_volume": cat_avg_vol if cat_avg_vol is not None else 0.0,
            # linear demand fields
            "lin_alpha": lin_alpha,
            "lin_beta": lin_beta,
            "lin_p_star": lin_p_star,
            "lin_est_demand": lin_est_demand,
            "lin_revenue": lin_rev,
            "warnings": warnings_cat + lin_warnings,
        }

    # Product-level stats (elasticity strictly from product observations; do NOT fallback to category elasticity)
    product_stats: Dict[str, Dict[str, Any]] = {}
    if name_col and name_col in df.columns:
        for prod, g in df.groupby(name_col):
            pkey = str(prod).strip()
            pairs = list(zip(g[price_col].astype(float).tolist(), g[qty_col].astype(float).tolist()))
            n_points = len(pairs)
            prod_el = None
            lin_alpha = None
            lin_beta = None
            lin_p_star = None
            lin_est_demand = None
            lin_rev = None
            prod_warnings = []
            if n_points >= 3:
                res = calculate_elasticity(pairs)
                prod_el = res.get("elasticity") if res.get("elasticity") == res.get("elasticity") else None
                # estimate linear demand per product
                lin = estimate_linear_demand(pairs)
                prod_warnings.extend(lin.get("warnings", []))
                lin_alpha = lin.get("alpha") if lin and lin.get("alpha") == lin.get("alpha") else None
                lin_beta = lin.get("beta") if lin and lin.get("beta") == lin.get("beta") else None
                if lin_alpha is not None and lin_beta is not None:
                    opt_lin = optimal_price_from_linear(lin_alpha, lin_beta)
                    prod_warnings.extend(opt_lin.get("warnings", []))
                    if opt_lin.get("valid"):
                        lin_p_star = float(opt_lin.get("p_star"))
                        lin_est_demand = lin_alpha + lin_beta * lin_p_star
                        if lin_est_demand is not None and lin_est_demand < 0:
                            prod_warnings.append("Estimated demand at linear optimal price is negative; clipped to 0")
                            lin_est_demand = 0.0
                        lin_rev = (lin_p_star * lin_est_demand) if lin_est_demand is not None else None
            prod_avg_vol = float(g[qty_col].astype(float).mean()) if n_points > 0 else 0.0
            product_stats[pkey] = {
                "elasticity": prod_el,
                "n_points": n_points,
                "avg_volume": prod_avg_vol,
                "lin_alpha": lin_alpha,
                "lin_beta": lin_beta,
                "lin_p_star": lin_p_star,
                "lin_est_demand": lin_est_demand,
                "lin_revenue": lin_rev,
                "warnings": prod_warnings,
            }
    else:
        # No product identifier column found — leave product_stats empty
        product_stats = {}

    # Prepare output dataframe and enrich rows
    df_out = df.copy()
    df_out["elasticidad_producto"] = None
    df_out["elasticidad_categoria"] = None
    df_out["volumen_promedio_producto"] = 0.0
    df_out["volumen_promedio_categoria"] = 0.0
    df_out["elasticidad_relativa"] = None
    df_out["volumen_relativo"] = None
    # New columns for strategic analysis
    df_out["recomendacion_precio"] = None
    df_out["rol_producto"] = None
    df_out["estrategia_recomendada"] = None
    df_out["estrategia_resumen"] = None
    # number of observations per product (helps debug why elasticity may be N/A)
    df_out["n_obs_producto"] = 0

    def summarize_by_role(role: Optional[str]) -> str:
        """Short strategy summary per role (<=10 words)."""
        mapping = {
            "Generador de ganancias": "Subir precio gradual, maximizar margen",
            "Estabilizador de ingresos": "Mantener premium, nicho leal",
            "Generador de trafico": "Precios competitivos y promociones",
            "Promesa de valor": "Precio competitivo, crecer volumen",
            "Sin clasificar": "Recolectar mas datos",
        }
        return mapping.get(role or "", "Estrategia general")

    for idx, row in df_out.iterrows():
        prod = row[name_col] if name_col and pd.notna(row.get(name_col)) else None
        # determine category for this row
        if cat_col and pd.notna(row.get(cat_col)):
            cat = row.get(cat_col)
        elif group_key == name_col:
            cat = prod
        else:
            cat = row.get(cat_col) if cat_col in row else None

        # use cleaned keys
        p_key = str(prod).strip() if prod is not None else None
        c_key = str(cat).strip() if cat is not None else None

        p_stats = product_stats.get(p_key, {}) if p_key is not None else {}
        c_stats = category_stats.get(c_key, {}) if c_key is not None else {}

        # product-level values (strictly product only)
        p_el = p_stats.get("elasticity")
        p_avg_vol = p_stats.get("avg_volume") if p_stats.get("avg_volume") is not None else 0.0

        # category-level values
        c_el = c_stats.get("elasticity")
        c_avg_vol = c_stats.get("avg_volume") if c_stats.get("avg_volume") is not None else 0.0

        # Elasticidad_producto must be computed only from product-level estimation (no fallback)
        if p_el is not None:
            try:
                product_el_out = round(float(p_el), 4)
            except Exception:
                product_el_out = "N/A"
        else:
            product_el_out = "N/A"

        # Elasticidad_categoria is always the category-level estimate when available
        if c_el is not None:
            try:
                category_el_out = round(float(c_el), 4)
            except Exception:
                category_el_out = "N/A"
        else:
            category_el_out = "N/A"

        # Relative elasticity: compute using raw numeric product and category elasticities when available
        if (isinstance(p_el, (int, float)) and isinstance(c_el, (int, float)) and c_el != 0):
            try:
                elasticidad_rel = round(float(p_el) / float(c_el), 4)
            except Exception:
                elasticidad_rel = "N/A"
        else:
            elasticidad_rel = "N/A"

        # Relative volume: product_avg_qty / category_avg_qty (use 'N/A' when category avg is zero or missing)
        try:
            p_avg = float(p_avg_vol) if p_avg_vol is not None else 0.0
            c_avg = float(c_avg_vol) if c_avg_vol is not None else 0.0
            volumen_rel = round(p_avg / c_avg, 4) if c_avg not in (None, 0.0) else "N/A"
        except Exception:
            volumen_rel = "N/A"

        # assign to dataframe
        df_out.at[idx, "elasticidad_producto"] = product_el_out
        df_out.at[idx, "elasticidad_categoria"] = category_el_out
        df_out.at[idx, "volumen_promedio_producto"] = round(float(p_avg_vol), 4) if p_avg_vol is not None else 0.0
        df_out.at[idx, "volumen_promedio_categoria"] = round(float(c_avg_vol), 4) if c_avg_vol is not None else 0.0
        df_out.at[idx, "elasticidad_relativa"] = elasticidad_rel
        df_out.at[idx, "volumen_relativo"] = volumen_rel
        df_out.at[idx, "n_obs_producto"] = int(p_stats.get("n_points", 0))

        # Use the analyze_product function to determine price recommendation, role, and strategy
        el_rel_num = elasticidad_rel if isinstance(elasticidad_rel, (int, float)) else None
        vol_rel_num = volumen_rel if isinstance(volumen_rel, (int, float)) else None

        price_rec, role, strategy = analyze_product(el_rel_num, vol_rel_num)

        df_out.at[idx, "recomendacion_precio"] = price_rec
        df_out.at[idx, "rol_producto"] = role
        df_out.at[idx, "estrategia_recomendada"] = strategy
        df_out.at[idx, "estrategia_resumen"] = summarize_by_role(role)

    # Round numeric columns for internal consistency
    for c in df_out.columns:
        if pd.api.types.is_numeric_dtype(df_out[c].dtype):
            df_out[c] = df_out[c].apply(lambda v: (round(float(v), 2) if v == v and v is not None else v))

    # Prepare an export dataframe where all numeric values are strings with two decimals
    df_export = df_out.copy()

    # Generate comprehensive pricing report with modern visualizations
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Use the modern report generator
    generate_pricing_report(df_out, uploads_dir, cat_col)

    # Collect generated assets to expose via API
    image_names = [
        "roles_plot.png",
        "roles_counts.png",
        "price_recommendations.png",
        "distribution_by_role.png",
    ]
    report_names = [
        "summary_stats.csv",
        "overall_summary.csv",
    ]

    image_urls: List[str] = []
    report_urls: List[str] = []
    for name in image_names:
        if (uploads_dir / name).exists():
            image_urls.append(f"/api/data/download/{name}")
    for name in report_names:
        if (uploads_dir / name).exists():
            report_urls.append(f"/api/data/download/{name}")

    def format_for_locale(v):
        """Format values for CSV export using comma as decimal separator and two decimals."""
        try:
            if v is None:
                return ""
            if isinstance(v, str) and v.strip().upper() == "N/A":
                return "N/A"
            if isinstance(v, (int, float)):
                if isinstance(v, float) and (v != v):
                    return ""
                return f"{v:.2f}".replace('.', ',')
            try:
                fv = float(str(v))
                if fv != fv:
                    return ""
                return f"{fv:.2f}".replace('.', ',')
            except Exception:
                return str(v)
        except Exception:
            return ""

    # Apply locale formatting to all columns
    for c in df_export.columns:
        df_export[c] = df_export[c].apply(format_for_locale)

    # Save resultado.csv file
    try:
        for p in uploads_dir.glob("*.csv"):
            try:
                p.unlink()
            except Exception:
                pass
    except Exception:
        pass

    try:
        resultado_path = uploads_dir / "resultado.csv"
        df_export.to_csv(resultado_path, index=False, sep=';')
        download_url = f"/api/data/download/{resultado_path.name}"
    except Exception:
        download_url = None

    # Build response warnings and matched columns info
    warnings: List[str] = [] if groups else ["No groups with >=3 observations found"]
    matched = {"price": price_col, "quantity": qty_col, "category": cat_col, "name": name_col, "date": date_col}
    warnings.extend([f"Matched {k} column: {v}" for k, v in matched.items() if v])
    if cost_col is None:
        warnings.append("No cost column detected; optimal_price not computed")

    # Build group_sample matching the response model
    group_sample: List[Dict[str, Any]] = []
    for cat, stats in category_stats.items():
        group_sample.append({
            "category": cat,
            "observations": int(stats.get("n_points", 0)),
            "elasticity": (round(float(stats["elasticity"]), 2) if stats.get("elasticity") is not None else None),
            "intercept": (round(float(stats["intercept"]), 2) if stats.get("intercept") is not None else None),
            "demand_factor": (round(float(stats["demand_factor"]), 2) if stats.get("demand_factor") is not None else None),
            "r2": round(float(stats.get("r2", 0.0)), 2),
            "n_points": int(stats.get("n_points", 0)),
            "warnings": stats.get("warnings", []),
        })

    return DataUploadResponse(
        rows_loaded=int(len(df)),
        grouped_levels=int(len(groups)),
        group_sample=group_sample,
        warnings=warnings,
        download_url=download_url,
        image_urls=image_urls,
        report_urls=report_urls,
    )


@router.get("/data/download/{filename}")
async def download_uploaded_file(filename: str):
    """Serve previously generated CSV files and images from the uploads/ directory with cache-busting headers."""
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    file_path = uploads_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type based on extension
    if filename.lower().endswith('.csv'):
        media_type = "text/csv"
    elif filename.lower().endswith('.png'):
        media_type = "image/png"
    else:
        media_type = "application/octet-stream"

    # Add timestamp to force fresh download and prevent caching
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) == 2:
        download_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
    else:
        download_filename = f"{filename}_{timestamp}"

    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.post("/optimize-price-linear", response_model=LinearOptimizationResponse)
async def optimize_price_linear_endpoint(payload: LinearOptimizationRequest) -> LinearOptimizationResponse:
    """Compute revenue-maximizing price under a linear demand assumption Q = alpha + beta * P."""
    try:
        warnings = []
        alpha = payload.alpha
        beta = payload.beta
        if (alpha is None or beta is None) and payload.observations:
            obs_tuples = [(o.price, o.quantity) for o in payload.observations]
            est = estimate_linear_demand(obs_tuples)
            warnings.extend(est.get("warnings", []))
            alpha = float(est.get("alpha", float("nan"))) if est.get("alpha") == est.get("alpha") else None
            beta = float(est.get("beta", float("nan"))) if est.get("beta") == est.get("beta") else None
            if est.get("n_points", 0) < 3:
                warnings.append("Insufficient observations to estimate linear demand")
        if alpha is None or beta is None:
            raise HTTPException(status_code=400, detail="Provide alpha and beta or at least 3 observations to estimate them")
        res = optimal_price_from_linear(alpha, beta)
        warnings.extend(res.get("warnings", []))
        if not res.get("valid", False):
            recommendation = "No se pudo calcular un precio óptimo bajo el modelo lineal. Revise los parámetros de demanda."
            return LinearOptimizationResponse(
                product_id=payload.product_id,
                optimal_price=None,
                current_price=round(payload.current_price, 2),
                estimated_demand=None,
                estimated_revenue=None,
                elasticity_at_optimal=None,
                recommendation=recommendation,
                warnings=warnings,
            )

        p_star = float(res["p_star"])
        estimated_demand = alpha + beta * p_star
        if estimated_demand < 0:
            warnings.append("Estimated demand at optimal price is negative; check demand parameters")
            estimated_demand = 0.0
        estimated_revenue = p_star * estimated_demand

        try:
            elasticity_at_optimal = (beta * p_star) / (alpha + beta * p_star) if (alpha + beta * p_star) != 0 else None
        except Exception:
            elasticity_at_optimal = None

        delta_pct = ((p_star - payload.current_price) / payload.current_price) * 100.0
        action = "Sube" if delta_pct > 0 else ("Baja" if delta_pct < 0 else "Mantén")
        recommendation = f"{action} precio {abs(round(delta_pct, 2)):.2f}% para maximizar ingresos (precio óptimo calculado)."

        if elasticity_at_optimal is not None:
            e = elasticity_at_optimal
            if e < -1:
                guidance = "Demanda elástica: reducir precio puede aumentar ingresos."
            elif e > -1 and e < 0:
                guidance = "Demanda inelástica: aumentar precio puede aumentar ingresos."
            else:
                guidance = "Elasticidad cercana a -1: ajustes de precio tendrán efecto neutro sobre ingresos."
            recommendation = recommendation + " " + guidance

        return LinearOptimizationResponse(
            product_id=payload.product_id,
            optimal_price=round(p_star, 2),
            current_price=round(payload.current_price, 2),
            estimated_demand=round(estimated_demand, 2),
            estimated_revenue=round(estimated_revenue, 2),
            elasticity_at_optimal=(round(elasticity_at_optimal, 2) if elasticity_at_optimal is not None else None),
            recommendation=recommendation,
            warnings=warnings,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error computing linear optimal price: {exc}")
