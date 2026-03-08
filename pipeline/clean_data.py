"""Data cleaning pipeline for assignment-compliant customer analytics datasets."""

from __future__ import annotations

import pandas as pd
from pipeline.utils import PROCESSED_DIR, ensure_processed_dir, read_csv


def _null_counts(df: pd.DataFrame) -> pd.Series:
    """Return null counts for all columns."""
    return df.isna().sum()


def _print_cleaning_report(
    dataset: str,
    rows_before: int,
    rows_after: int,
    duplicates_removed: int,
    null_before: pd.Series,
    null_after: pd.Series,
) -> None:
    """Print standardized cleaning report to stdout."""
    print(f"\n[{dataset}]")
    print(f"rows before: {rows_before}")
    print(f"rows after: {rows_after}")
    print(f"duplicate rows removed: {duplicates_removed}")
    print("null counts before:")
    print(null_before.to_string())
    print("null counts after:")
    print(null_after.to_string())


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all required cleaning rules for customers dataset."""
    cleaned = df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]

    cleaned["name"] = cleaned["name"].astype("string").str.strip()
    cleaned["region"] = cleaned["region"].astype("string").str.strip()
    cleaned["region"] = cleaned["region"].replace("", pd.NA).fillna("Unknown")

    cleaned["email"] = cleaned["email"].astype("string").str.strip().str.lower()
    cleaned["signup_date"] = pd.to_datetime(cleaned["signup_date"], errors="coerce")

    email_present = cleaned["email"].notna() & (cleaned["email"].str.len() > 0)
    has_at = cleaned["email"].str.contains("@", regex=False, na=False)
    has_dot = cleaned["email"].str.contains(".", regex=False, na=False)
    cleaned["is_valid_email"] = email_present & has_at & has_dot

    before_dedup = len(cleaned)
    cleaned = cleaned.sort_values("signup_date", na_position="first")
    cleaned = cleaned.drop_duplicates(subset=["customer_id"], keep="last")
    cleaned = cleaned.reset_index(drop=True)
    cleaned.attrs["duplicates_removed"] = before_dedup - len(cleaned)

    return cleaned


def _parse_order_dates(order_date: pd.Series) -> pd.Series:
    """Parse order_date with supported assignment formats."""
    text = order_date.astype("string").str.strip()

    parsed = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    parsed = parsed.fillna(pd.to_datetime(text, format="%d/%m/%Y", errors="coerce"))
    parsed = parsed.fillna(pd.to_datetime(text, format="%m-%d-%Y", errors="coerce"))

    return parsed


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all required cleaning rules for orders dataset."""
    cleaned = df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]

    before_drop = len(cleaned)
    both_ids_null = cleaned["order_id"].isna() & cleaned["customer_id"].isna()
    cleaned = cleaned.loc[~both_ids_null].copy()
    cleaned.attrs["duplicates_removed"] = before_drop - len(cleaned)

    cleaned["order_date"] = _parse_order_dates(cleaned["order_date"])
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")

    product_median = cleaned.groupby("product")["amount"].transform("median")
    cleaned["amount"] = cleaned["amount"].fillna(product_median)

    cleaned["status"] = cleaned["status"].astype("string").str.strip().str.lower()
    cleaned["status"] = cleaned["status"].replace({"done": "completed", "canceled": "cancelled"})
    allowed_status = {"completed", "pending", "cancelled", "refunded"}
    cleaned["status"] = cleaned["status"].where(cleaned["status"].isin(allowed_status), "pending")

    cleaned["order_year_month"] = cleaned["order_date"].dt.strftime("%Y-%m")

    cleaned = cleaned.reset_index(drop=True)
    return cleaned


def run_cleaning() -> None:
    """Run full cleaning flow and persist cleaned datasets."""
    ensure_processed_dir()

    raw_customers = read_csv("customers.csv")
    raw_orders = read_csv("orders.csv")

    customers_rows_before = len(raw_customers)
    customers_null_before = _null_counts(raw_customers)
    customers_clean = clean_customers(raw_customers)
    customers_rows_after = len(customers_clean)
    customers_null_after = _null_counts(customers_clean)

    orders_rows_before = len(raw_orders)
    orders_null_before = _null_counts(raw_orders)
    orders_clean = clean_orders(raw_orders)
    orders_rows_after = len(orders_clean)
    orders_null_after = _null_counts(orders_clean)

    customers_clean.to_csv(
        PROCESSED_DIR / "customers_clean.csv",
        index=False,
        date_format="%Y-%m-%d",
    )
    orders_clean.to_csv(
        PROCESSED_DIR / "orders_clean.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    _print_cleaning_report(
        dataset="customers",
        rows_before=customers_rows_before,
        rows_after=customers_rows_after,
        duplicates_removed=customers_clean.attrs.get("duplicates_removed", 0),
        null_before=customers_null_before,
        null_after=customers_null_after,
    )
    _print_cleaning_report(
        dataset="orders",
        rows_before=orders_rows_before,
        rows_after=orders_rows_after,
        duplicates_removed=orders_clean.attrs.get("duplicates_removed", 0),
        null_before=orders_null_before,
        null_after=orders_null_after,
    )


if __name__ == "__main__":
    run_cleaning()
