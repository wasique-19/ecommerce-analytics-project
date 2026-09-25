"""
DAY 5: Final Dashboard + Report
----------------------------------
- Builds one combined multi-panel PNG dashboard from all prior analysis
- Generates a final Markdown business report summarizing insights

Run:
    python src/day5_dashboard_report.py
(Run after day1-day4 scripts, since it reuses their CSV outputs.)
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
CHARTS_DIR = BASE_DIR / "outputs" / "charts"

sns.set_theme(style="whitegrid")


def build_dashboard():
    df = pd.read_csv(DATA_DIR / "cleaned_ecommerce_data.csv", parse_dates=["order_date"])
    rfm = pd.read_csv(REPORTS_DIR / "customer_rfm_segments.csv")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("E-Commerce Analytics Dashboard", fontsize=18, fontweight="bold")

    # Panel 1: Monthly revenue
    monthly = df.set_index("order_date").resample("ME")["revenue"].sum()
    axes[0, 0].plot(monthly.index, monthly.values, marker="o", color="#2E86AB")
    axes[0, 0].set_title("Monthly Revenue Trend")
    axes[0, 0].tick_params(axis="x", rotation=30)

    # Panel 2: Revenue by category
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    sns.barplot(x=cat_rev.values, y=cat_rev.index, ax=axes[0, 1], hue=cat_rev.index,
                palette="viridis", legend=False)
    axes[0, 1].set_title("Revenue by Category")

    # Panel 3: Customer segments
    seg_counts = rfm["segment"].value_counts()
    axes[1, 0].pie(seg_counts.values, labels=seg_counts.index, autopct="%1.0f%%",
                   colors=sns.color_palette("Set2"))
    axes[1, 0].set_title("Customer Segments (RFM)")

    # Panel 4: Revenue by city
    city_rev = df.groupby("city")["revenue"].sum().sort_values(ascending=False)
    sns.barplot(x=city_rev.index, y=city_rev.values, ax=axes[1, 1], hue=city_rev.index,
                palette="crest", legend=False)
    axes[1, 1].set_title("Revenue by City")
    axes[1, 1].tick_params(axis="x", rotation=30)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_path = CHARTS_DIR / "full_dashboard.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def build_report():
    df = pd.read_csv(DATA_DIR / "cleaned_ecommerce_data.csv", parse_dates=["order_date"])
    rfm = pd.read_csv(REPORTS_DIR / "customer_rfm_segments.csv")
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    top_products = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(5)
    seg_summary = rfm.groupby("segment")["customer_id"].count().sort_values(ascending=False)

    total_revenue = df["revenue"].sum()
    total_orders = df["order_id"].nunique()
    unique_customers = df["customer_id"].nunique()
    avg_order_value = df.groupby("order_id")["revenue"].sum().mean()

    lines = []
    lines.append("# E-Commerce Analytics — Final Report\n")
    lines.append(f"_Generated on {datetime.now().strftime('%Y-%m-%d')}_\n")
    lines.append("## 1. Key Metrics\n")
    lines.append(f"- **Total Revenue:** {total_revenue:,.2f}")
    lines.append(f"- **Total Orders:** {total_orders:,}")
    lines.append(f"- **Unique Customers:** {unique_customers:,}")
    lines.append(f"- **Average Order Value:** {avg_order_value:,.2f}\n")

    lines.append("## 2. Revenue by Category\n")
    for cat, val in cat_rev.items():
        lines.append(f"- {cat}: {val:,.2f}")

    lines.append("\n## 3. Top 5 Products by Revenue\n")
    for prod, val in top_products.items():
        lines.append(f"- {prod}: {val:,.2f}")

    lines.append("\n## 4. Customer Segmentation (RFM)\n")
    for seg, count in seg_summary.items():
        lines.append(f"- {seg}: {count} customers")

    lines.append("\n## 5. Dashboard\n")
    lines.append("See `outputs/charts/full_dashboard.png` for the combined visual dashboard.")
    lines.append("Individual charts are available in `outputs/charts/`.\n")

    lines.append("## 6. Recommendations\n")
    lines.append("- Focus retention campaigns on the **At Risk** and **Lost/Churned** segments.")
    lines.append("- Double down on the top-performing category and products for inventory planning.")
    lines.append("- Investigate low-revenue cities for potential marketing expansion.")

    report_path = REPORTS_DIR / "final_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    return report_path


if __name__ == "__main__":
    dashboard_path = build_dashboard()
    report_path = build_report()
    print(f"Dashboard saved to: {dashboard_path}")
    print(f"Final report saved to: {report_path}")
