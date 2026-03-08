import pandas as pd
from pipeline.clean_data import clean_customers, clean_orders, clean_products


def test_clean_customers_deduplicates_and_normalizes_email():
    df = pd.DataFrame(
        [
            {"customer_id": 1, "email": "TEST@EMAIL.COM "},
            {"customer_id": 1, "email": "test@email.com"},
        ]
    )
    out = clean_customers(df)
    assert len(out) == 1
    assert out.iloc[0]["email"] == "test@email.com"


def test_clean_orders_adds_revenue():
    df = pd.DataFrame(
        [{"order_id": 1, "order_date": "2025-01-01", "quantity": 2, "unit_price": 10.5}]
    )
    out = clean_orders(df)
    assert out.iloc[0]["revenue"] == 21.0


def test_clean_products_fills_category():
    df = pd.DataFrame([{"product_id": 10, "category": None}])
    out = clean_products(df)
    assert out.iloc[0]["category"] == "Unknown"
