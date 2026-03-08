"""Generate synthetic raw datasets for the customer analytics pipeline.

Run with:
    python -m pipeline.generate_sample_data
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"


def _random_dates(
    rng: np.random.Generator,
    n: int,
    start: str,
    end: str,
) -> pd.Series:
    """Create random dates between start and end (inclusive)."""
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    day_span = (end_ts - start_ts).days
    offsets = rng.integers(0, day_span + 1, size=n)
    return pd.Series(start_ts + pd.to_timedelta(offsets, unit="D"))


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    """Generate customers with duplicates and intentionally dirty values."""
    n_customers = 200

    first_names = np.array(
        [
            "Aarav",
            "Vihaan",
            "Anaya",
            "Ishaan",
            "Maya",
            "Arjun",
            "Diya",
            "Kabir",
            "Riya",
            "Aditya",
            "Neha",
            "Rahul",
            "Priya",
            "Karan",
            "Nisha",
            "Sonia",
            "Rohan",
            "Meera",
            "Aisha",
            "Dev",
        ]
    )
    last_names = np.array(
        [
            "Sharma",
            "Patel",
            "Gupta",
            "Singh",
            "Khan",
            "Iyer",
            "Reddy",
            "Das",
            "Nair",
            "Mehta",
            "Kapoor",
            "Joshi",
            "Bose",
            "Chopra",
            "Malhotra",
        ]
    )
    regions = np.array(["North", "South", "East", "West", ""])

    customer_ids = np.arange(1, n_customers + 1)
    chosen_first = rng.choice(first_names, size=n_customers)
    chosen_last = rng.choice(last_names, size=n_customers)
    names = pd.Series(chosen_first + " " + chosen_last)

    emails = (
        names.str.lower()
        .str.replace(" ", ".", regex=False)
        + pd.Series(customer_ids.astype(str))
        + "@example.com"
    )
    emails = pd.Series(emails, dtype="string")

    # Introduce missing and malformed emails for downstream validation checks.
    missing_idx = rng.choice(n_customers, size=16, replace=False)
    remaining_idx = np.setdiff1d(np.arange(n_customers), missing_idx)
    malformed_idx = rng.choice(remaining_idx, size=14, replace=False)
    malformed_variants = np.array(
        [
            "invalid_email",
            "userexample.com",
            "user@invalid",
            "noatsymbol.com",
            "bad.domain@",
        ]
    )

    emails.iloc[missing_idx] = pd.NA
    emails.iloc[malformed_idx] = rng.choice(malformed_variants, size=len(malformed_idx))

    signup_dates = _random_dates(rng, n_customers, "2022-01-01", "2024-12-31")

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "name": names,
            "email": emails,
            "region": rng.choice(
                regions,
                size=n_customers,
                p=[0.24, 0.24, 0.24, 0.24, 0.04],
            ),
            "signup_date": signup_dates.dt.strftime("%Y-%m-%d"),
        }
    )

    # Add 10 duplicate customer_id rows with different signup_date values.
    duplicate_ids = rng.choice(customer_ids, size=10, replace=False)
    duplicate_rows = customers[customers["customer_id"].isin(duplicate_ids)].copy()
    duplicate_rows["signup_date"] = _random_dates(
        rng,
        len(duplicate_rows),
        "2022-01-01",
        "2024-12-31",
    ).dt.strftime("%Y-%m-%d")

    customers_with_dups = pd.concat([customers, duplicate_rows], ignore_index=True)
    customers_with_dups = customers_with_dups.sample(
        frac=1.0,
        random_state=42,
    ).reset_index(drop=True)
    return customers_with_dups


def generate_products(rng: np.random.Generator) -> pd.DataFrame:
    """Generate product catalog with fixed categories and realistic prices."""
    n_products = 15
    categories = np.array(["Electronics", "Clothing", "Home", "Sports"])
    product_names = np.array(
        [
            "Wireless Earbuds",
            "Smart Watch",
            "Bluetooth Speaker",
            "Running Shoes",
            "Yoga Mat",
            "Winter Jacket",
            "Office Chair",
            "Coffee Maker",
            "Air Purifier",
            "Backpack",
            "Fitness Tracker",
            "Table Lamp",
            "Cookware Set",
            "Football",
            "Hoodie",
        ]
    )

    unit_prices = rng.uniform(10, 500, size=n_products).round(2)
    products = pd.DataFrame(
        {
            "product_id": np.arange(1, n_products + 1),
            "product_name": product_names,
            "category": rng.choice(categories, size=n_products),
            "unit_price": unit_prices,
        }
    )
    return products


def generate_orders(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Generate orders with missing amounts, mixed date formats, and status variants."""
    n_orders = 1000
    statuses = np.array(
        ["completed", "pending", "cancelled", "refunded", "done", "canceled"]
    )

    order_ids = np.arange(1, n_orders + 1)
    customer_pool = customers["customer_id"].dropna().unique()
    product_pool = products["product_name"].values

    orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "customer_id": rng.choice(customer_pool, size=n_orders),
            "product": rng.choice(product_pool, size=n_orders),
            "status": rng.choice(
                statuses,
                size=n_orders,
                p=[0.45, 0.18, 0.14, 0.08, 0.08, 0.07],
            ),
        }
    )

    # Amount is based on product price with quantity and small random variation.
    price_lookup = products.set_index("product_name")["unit_price"]
    base_price = orders["product"].map(price_lookup).astype(float)
    quantity_factor = rng.integers(1, 5, size=n_orders)
    noise_multiplier = rng.uniform(0.9, 1.15, size=n_orders)
    orders["amount"] = (base_price * quantity_factor * noise_multiplier).round(2)

    # Introduce missing amounts for cleaning-stage median fill checks.
    missing_amount_idx = rng.choice(n_orders, size=85, replace=False)
    orders.loc[missing_amount_idx, "amount"] = np.nan

    order_dates = _random_dates(rng, n_orders, "2022-01-01", "2024-12-31")
    format_choice = rng.choice(np.array([0, 1, 2]), size=n_orders, p=[0.4, 0.3, 0.3])
    fmt_ymd = order_dates.dt.strftime("%Y-%m-%d")
    fmt_dmy = order_dates.dt.strftime("%d/%m/%Y")
    fmt_mdy = order_dates.dt.strftime("%m-%d-%Y")
    orders["order_date"] = np.where(
        format_choice == 0,
        fmt_ymd,
        np.where(format_choice == 1, fmt_dmy, fmt_mdy),
    )

    return orders[
        ["order_id", "customer_id", "product", "amount", "order_date", "status"]
    ]


def main() -> None:
    """Generate and persist all raw datasets."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)

    customers = generate_customers(rng)
    products = generate_products(rng)
    orders = generate_orders(rng, customers, products)

    customers.to_csv(RAW_DIR / "customers.csv", index=False)
    products.to_csv(RAW_DIR / "products.csv", index=False)
    orders.to_csv(RAW_DIR / "orders.csv", index=False)

    print("Synthetic datasets generated:")
    print(f"- {RAW_DIR / 'customers.csv'} ({len(customers)} rows)")
    print(f"- {RAW_DIR / 'products.csv'} ({len(products)} rows)")
    print(f"- {RAW_DIR / 'orders.csv'} ({len(orders)} rows)")


if __name__ == "__main__":
    main()
