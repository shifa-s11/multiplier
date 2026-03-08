from __future__ import annotations

from pathlib import Path

import pandas as pd


class DataService:
    """Service layer for loading processed analytics CSV outputs."""

    BASE_DIR = Path(__file__).resolve().parents[2]
    PROCESSED_DIR = BASE_DIR / "data" / "processed"

    @classmethod
    def _load_csv(cls, filename: str) -> list[dict]:
        """Load a processed CSV file and return records for JSON responses."""
        file_path = cls.PROCESSED_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError("Data file not found")

        df = pd.read_csv(file_path)
        return df.to_dict(orient="records")

    @classmethod
    def get_monthly_revenue(cls) -> list[dict]:
        return cls._load_csv("monthly_revenue.csv")

    @classmethod
    def get_top_customers(cls) -> list[dict]:
        return cls._load_csv("top_customers.csv")

    @classmethod
    def get_category_performance(cls) -> list[dict]:
        return cls._load_csv("category_performance.csv")

    @classmethod
    def get_regional_analysis(cls) -> list[dict]:
        return cls._load_csv("regional_analysis.csv")
