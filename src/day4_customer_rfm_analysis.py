"""
DAY 4: Customer Analysis (RFM Segmentation)
---------------------------------------------
- Loads cleaned data
- Computes Recency, Frequency, Monetary (RFM) scores per customer
- Segments customers into groups: Champions, Loyal, At Risk, Lost, etc.
- Saves the segmented customer table + a segment summary

Run:
    python src/day4_customer_rfm_analysis.py
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "cleaned_ecommerce_data.csv", parse_dates=["order_date"])


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
    ).reset_index()

    # Score each dimension 1-4 using quartiles (4 = best)
    rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)

    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    def segment(row):
        if row["rfm_score"] >= 10:
            return "Champions"
        elif row["rfm_score"] >= 8:
            return "Loyal Customers"
        elif row["rfm_score"] >= 6:
            return "Potential Loyalists"
        elif row["rfm_score"] >= 4:
            return "At Risk"
        else:
            return "Lost / Churned"

    rfm["segment"] = rfm.apply(segment, axis=1)
    return rfm


if __name__ == "__main__":
    data = load_data()
    rfm_df = compute_rfm(data)

    rfm_path = REPORTS_DIR / "customer_rfm_segments.csv"
    rfm_df.to_csv(rfm_path, index=False)

    segment_summary = (
        rfm_df.groupby("segment")
        .agg(customers=("customer_id", "count"), avg_monetary=("monetary", "mean"))
        .sort_values("avg_monetary", ascending=False)
    )
    segment_summary.to_csv(REPORTS_DIR / "segment_summary.csv")

    print("Customer segments:")
    print(segment_summary)
    print(f"\nFull RFM table saved to: {rfm_path}")
