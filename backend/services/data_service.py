from __future__ import annotations

import csv
from pathlib import Path


class DataService:
    """Service layer for loading processed analytics CSV outputs."""

    BASE_DIR = Path(__file__).resolve().parents[2]
    PROCESSED_DIR = BASE_DIR / "data" / "processed"

    @staticmethod
    def _coerce_value(value: str):
        """Best-effort conversion for JSON-friendly primitive types."""
        if value is None:
            return None

        text = value.strip()
        if text == "":
            return None

        lower = text.lower()
        if lower == "true":
            return True
        if lower == "false":
            return False

        try:
            if "." not in text:
                return int(text)
            return float(text)
        except ValueError:
            return text

    @classmethod
    def _load_csv(cls, filename: str) -> list[dict]:
        """Load a processed CSV file and return records for JSON responses."""
        file_path = cls.PROCESSED_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError("Data file not found")

        with file_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
            rows = csv.DictReader(csv_file)
            return [
                {key: cls._coerce_value(value) for key, value in row.items()}
                for row in rows
            ]

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
