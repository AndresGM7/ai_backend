import io
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

pytest.skip("upload/download endpoints omitted in public branch", allow_module_level=True)


def _upload(csv_text: str):
    file_obj = io.BytesIO(csv_text.encode("utf-8"))
    return client.post(
        "/api/data/upload",
        files={"file": ("data.csv", file_obj, "text/csv")}
    )


def test_upload_minimal_spanish_columns():
    # Using precio, cantidad and descripcion (name fallback) with >=3 rows
    csv_data = (
        "precio,cantidad,descripcion\n"
        "100,5,Producto A\n"
        "120,4,Producto A\n"
        "140,3,Producto A\n"
        "200,2,Producto B\n"
    )
    resp = _upload(csv_data)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["rows_loaded"] >= 4
    assert data["grouped_levels"] >= 1
    assert any("Matched price column" in w for w in data["warnings"]) or any("precio" in w for w in data["warnings"])  # informative


def test_upload_with_category_synonyms():
    # Using categoria, qty, prc synonyms, two categories each >=3 rows
    csv_data = (
        "categoria,qty,prc,fecha\n"
        "Electronics,5,100,2025-01-01\n"
        "Electronics,4,120,2025-01-02\n"
        "Electronics,3,140,2025-01-03\n"
        "Ropa,6,60,2025-01-01\n"
        "Ropa,5,55,2025-01-02\n"
        "Ropa,4,50,2025-01-03\n"
    )
    resp = _upload(csv_data)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["grouped_levels"] >= 2
    # Ensure warnings list matched columnas
    assert any("Matched category column" in w for w in data["warnings"]) or any("categoria" in w for w in data["warnings"])


def test_upload_requires_price_and_quantity():
    # Missing quantity synonym
    csv_data = "precio,descripcion\n100,Producto A\n120,Producto A\n140,Producto A\n"
    resp = _upload(csv_data)
    assert resp.status_code == 400
    assert "Missing required columns" in resp.text
