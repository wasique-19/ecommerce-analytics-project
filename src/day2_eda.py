"""
DAY 2: Exploratory Data Analysis (EDA)
---------------------------------------
- Loads cleaned data
- Computes summary statistics, revenue breakdowns, and trends
- Saves the key numeric findings as CSVs (used by Day 3 charts + Day 5 report)

Run:
    python src/day2_eda.py
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "cleaned_ecommerce_data.csv", parse_dates=["order_date"])
    return df


def run_eda(df: pd.DataFrame):
    summary_lines = []

    total_revenue = df["revenue"].sum()
    total_orders = df["order_id"].nunique()
    avg_order_value = df.groupby("order_id")["revenue"].sum().mean()
    unique_customers = df["customer_id"].nunique()

    summary_lines.append(f"Total Revenue: {total_revenue:,.2f}")
    summary_lines.append(f"Total Orders: {total_orders:,}")
    summary_lines.append(f"Unique Customers: {unique_customers:,}")
    summary_lines.append(f"Average Order Value: {avg_order_value:,.2f}")

    # Revenue by category
    revenue_by_category = (
        df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    )
    revenue_by_category.to_csv(REPORTS_DIR / "revenue_by_category.csv")

    # Top 10 products by revenue
    top_products = (
        df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(10)
    )
    top_products.to_csv(REPORTS_DIR / "top_products.csv")

    # Revenue by city
    revenue_by_city = df.groupby("city")["revenue"].sum().sort_values(ascending=False)
    revenue_by_city.to_csv(REPORTS_DIR / "revenue_by_city.csv")

    # Payment method distribution
    payment_dist = df["payment_method"].value_counts()
    payment_dist.to_csv(REPORTS_DIR / "payment_method_distribution.csv")

    # Monthly revenue trend
    monthly_revenue = (
        df.set_index("order_date").resample("ME")["revenue"].sum()
    )
    monthly_revenue.to_csv(REPORTS_DIR / "monthly_revenue_trend.csv")

    # Average rating by category
    avg_rating = df.groupby("category")["rating"].mean().sort_values(ascending=False)
    avg_rating.to_csv(REPORTS_DIR / "avg_rating_by_category.csv")

    # Save the text summary
    with open(REPORTS_DIR / "eda_summary.txt", "w") as f:
        f.write("EDA SUMMARY\n")
        f.write("===========\n")
        f.write("\n".join(summary_lines))
        f.write("\n\nTop Category by Revenue:\n")
        f.write(str(revenue_by_category.head(3)))
        f.write("\n\nTop 5 Products by Revenue:\n")
        f.write(str(top_products.head(5)))

    print("\n".join(summary_lines))
    print("\nEDA outputs saved in outputs/reports/")


if __name__ == "__main__":
    data = load_data()
    run_eda(data)
