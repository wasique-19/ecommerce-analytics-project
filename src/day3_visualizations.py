"""
DAY 3: Visualizations
-----------------------
- Loads cleaned data
- Generates key charts and saves them as PNGs in outputs/charts/

Run:
    python src/day3_visualizations.py
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = BASE_DIR / "outputs" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "cleaned_ecommerce_data.csv", parse_dates=["order_date"])


def plot_monthly_revenue(df):
    monthly = df.set_index("order_date").resample("ME")["revenue"].sum()
    plt.figure(figsize=(10, 5))
    monthly.plot(marker="o", color="#2E86AB")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "monthly_revenue_trend.png", dpi=150)
    plt.close()


def plot_revenue_by_category(df):
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=cat_rev.values, y=cat_rev.index, hue=cat_rev.index, palette="viridis", legend=False)
    plt.title("Revenue by Category")
    plt.xlabel("Revenue")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "revenue_by_category.png", dpi=150)
    plt.close()


def plot_top_products(df):
    top = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top.values, y=top.index, hue=top.index, palette="mako", legend=False)
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "top_10_products.png", dpi=150)
    plt.close()


def plot_payment_methods(df):
    counts = df["payment_method"].value_counts()
    plt.figure(figsize=(7, 7))
    plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
            colors=sns.color_palette("pastel"))
    plt.title("Payment Method Distribution")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "payment_method_distribution.png", dpi=150)
    plt.close()


def plot_revenue_by_city(df):
    city_rev = df.groupby("city")["revenue"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=city_rev.index, y=city_rev.values, hue=city_rev.index, palette="crest", legend=False)
    plt.title("Revenue by City")
    plt.xlabel("City")
    plt.ylabel("Revenue")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "revenue_by_city.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    data = load_data()
    plot_monthly_revenue(data)
    plot_revenue_by_category(data)
    plot_top_products(data)
    plot_payment_methods(data)
    plot_revenue_by_city(data)
    print(f"5 charts saved in: {CHARTS_DIR}")
