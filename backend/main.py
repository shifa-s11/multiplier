from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.services.data_service import DataService

app = FastAPI(title="Customer Analytics API", version="1.0.0")

# Enable CORS so dashboard frontend can call the API from a different origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _safe_load(loader) -> list[dict]:
    """Translate missing CSV files into assignment-specified HTTP 404 responses."""
    try:
        return loader()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/api/revenue")
def get_revenue() -> list[dict]:
    return _safe_load(DataService.get_monthly_revenue)


@app.get("/api/top-customers")
def get_top_customers() -> list[dict]:
    return _safe_load(DataService.get_top_customers)


@app.get("/api/categories")
def get_categories() -> list[dict]:
    return _safe_load(DataService.get_category_performance)


@app.get("/api/regions")
def get_regions() -> list[dict]:
    return _safe_load(DataService.get_regional_analysis)
