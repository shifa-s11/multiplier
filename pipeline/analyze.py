"""Analysis stage for customer analytics pipeline assignment."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV safely, handling missing files and empty files."""
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"File not found: {path}")
    except pd.errors.EmptyDataError:
        print(f"Empty CSV file: {path}")
    return pd.DataFrame()


def merge_datasets(
    orders_clean: pd.DataFrame,
    customers_clean: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Perform required left joins and print unmatched merge counts."""
    orders_customer_merged = pd.merge(
        orders_clean,
        customers_clean,
        how="left",
        on="customer_id",
        indicator=True,
    )
    orders_without_customer = (orders_customer_merged["_merge"] == "left_only").sum()
    orders_with_customers = orders_customer_merged.drop(columns=["_merge"])

    full_merged = pd.merge(
        orders_with_customers,
        products,
        how="left",
        left_on="product",
        right_on="product_name",
        indicator=True,
    )
    orders_without_product = (full_merged["_merge"] == "left_only").sum()
    full_data = full_merged.drop(columns=["_merge"])

    print(f"number of orders without matching customer: {int(orders_without_customer)}")
    print(f"number of orders without matching product: {int(orders_without_product)}")

    return full_data


def compute_churn_by_customer(
    full_data: pd.DataFrame,
    customers_clean: pd.DataFrame,
) -> pd.DataFrame:
    """Mark churned customers based on no completed order in the last 90 days."""
    churn_base = customers_clean[["customer_id"]].drop_duplicates().copy()

    working = full_data.copy()
    working["order_date"] = pd.to_datetime(working["order_date"], errors="coerce")
    latest_order_date = working["order_date"].max()

    completed = working.loc[
        working["status"] == "completed",
        ["customer_id", "order_date"],
    ]
    latest_completed_per_customer = completed.groupby(
        "customer_id",
        as_index=False,
    )["order_date"].max()
    latest_completed_per_customer = latest_completed_per_customer.rename(
        columns={"order_date": "last_completed_order_date"}
    )

    churn = pd.merge(
        churn_base,
        latest_completed_per_customer,
        how="left",
        on="customer_id",
    )

    if pd.isna(latest_order_date):
        churn["churned"] = True
    else:
        cutoff_date = latest_order_date - pd.Timedelta(days=90)
        churn["churned"] = churn["last_completed_order_date"].isna() | (
            churn["last_completed_order_date"] < cutoff_date
        )

    return churn[["customer_id", "churned"]]


def build_monthly_revenue(full_data: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue trend using completed orders only."""
    completed = full_data.loc[full_data["status"] == "completed"].copy()
    completed["amount"] = pd.to_numeric(completed["amount"], errors="coerce").fillna(0)

    monthly_revenue = (
        completed.groupby("order_year_month", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_revenue"})
        .sort_values("order_year_month")
    )
    return monthly_revenue


def build_top_customers(
    full_data: pd.DataFrame,
    churn_df: pd.DataFrame,
) -> pd.DataFrame:
    """Top 10 customers by completed-order spend, including churn indicator."""
    completed = full_data.loc[full_data["status"] == "completed"].copy()
    completed["amount"] = pd.to_numeric(completed["amount"], errors="coerce").fillna(0)
    completed["region"] = completed["region"].fillna("Unknown")

    top_customers = (
        completed.groupby(["customer_id", "name", "region"], as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_spend"})
        .sort_values("total_spend", ascending=False)
        .head(10)
    )

    top_customers = pd.merge(top_customers, churn_df, how="left", on="customer_id")
    top_customers["churned"] = top_customers["churned"].fillna(True)
    return top_customers


def build_category_performance(full_data: pd.DataFrame) -> pd.DataFrame:
    """Category-level revenue, order value, and order count metrics."""
    working = full_data.copy()
    working["amount"] = pd.to_numeric(working["amount"], errors="coerce").fillna(0)
    working["category"] = working["category"].fillna("Unknown")

    category_performance = (
        working.groupby("category", as_index=False)
        .agg(
            total_revenue=("amount", "sum"),
            average_order_value=("amount", "mean"),
            number_of_orders=("order_id", "count"),
        )
        .sort_values("total_revenue", ascending=False)
    )
    return category_performance


def build_regional_analysis(
    full_data: pd.DataFrame,
    customers_clean: pd.DataFrame,
) -> pd.DataFrame:
    """Regional customer/order/revenue metrics with average revenue per customer."""
    customers = customers_clean.copy()
    customers["region"] = customers["region"].fillna("Unknown")

    orders = full_data.copy()
    orders["region"] = orders["region"].fillna("Unknown")
    orders["amount"] = pd.to_numeric(orders["amount"], errors="coerce").fillna(0)

    customers_by_region = (
        customers.groupby("region", as_index=False)["customer_id"]
        .nunique()
        .rename(columns={"customer_id": "number_of_customers"})
    )

    orders_by_region = (
        orders.groupby("region", as_index=False)
        .agg(number_of_orders=("order_id", "count"), total_revenue=("amount", "sum"))
    )

    regional_analysis = pd.merge(
        customers_by_region,
        orders_by_region,
        how="outer",
        on="region",
    )
    regional_analysis["number_of_customers"] = (
        regional_analysis["number_of_customers"].fillna(0).astype(int)
    )
    regional_analysis["number_of_orders"] = (
        regional_analysis["number_of_orders"].fillna(0).astype(int)
    )
    regional_analysis["total_revenue"] = regional_analysis["total_revenue"].fillna(0)

    regional_analysis["average_revenue_per_customer"] = (
        regional_analysis["total_revenue"]
        .div(regional_analysis["number_of_customers"].replace(0, pd.NA))
        .fillna(0)
    )

    regional_analysis = regional_analysis[
        [
            "region",
            "number_of_customers",
            "number_of_orders",
            "total_revenue",
            "average_revenue_per_customer",
        ]
    ].sort_values("total_revenue", ascending=False)

    return regional_analysis


def run_analysis() -> None:
    """Run all assignment analysis tasks and save output CSV files."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    customers_clean = load_csv(PROCESSED_DIR / "customers_clean.csv")
    orders_clean = load_csv(PROCESSED_DIR / "orders_clean.csv")
    products = load_csv(RAW_DIR / "products.csv")

    if customers_clean.empty or orders_clean.empty or products.empty:
        print("Analysis skipped due to missing or empty input files.")
        return

    full_data = merge_datasets(
        orders_clean=orders_clean,
        customers_clean=customers_clean,
        products=products,
    )

    churn_df = compute_churn_by_customer(
        full_data=full_data,
        customers_clean=customers_clean,
    )
    monthly_revenue = build_monthly_revenue(full_data)
    top_customers = build_top_customers(full_data, churn_df)
    category_performance = build_category_performance(full_data)
    regional_analysis = build_regional_analysis(full_data, customers_clean)

    monthly_revenue.to_csv(PROCESSED_DIR / "monthly_revenue.csv", index=False)
    top_customers.to_csv(PROCESSED_DIR / "top_customers.csv", index=False)
    category_performance.to_csv(PROCESSED_DIR / "category_performance.csv", index=False)
    regional_analysis.to_csv(PROCESSED_DIR / "regional_analysis.csv", index=False)

    print("Analysis files written to data/processed")


if __name__ == "__main__":
    run_analysis()
