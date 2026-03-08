"""Utility helpers for file paths and common IO operations."""

from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


def ensure_processed_dir() -> None:
    """Create processed directory if it does not exist."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(filename: str) -> pd.DataFrame:
    """Read a CSV from the raw data directory."""
    return pd.read_csv(RAW_DIR / filename)
