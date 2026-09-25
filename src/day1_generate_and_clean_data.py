"""
DAY 1: Data Generation & Cleaning
---------------------------------
- Generates a realistic (synthetic) e-commerce orders dataset
- Intentionally injects real-world dirtiness (nulls, duplicates, bad types,
  inconsistent casing) so that the cleaning step has real work to do
- Cleans the data and saves it to data/cleaned_ecommerce_data.csv

Run:
    python src/day1_generate_and_clean_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

N_ORDERS = 5000

CATEGORIES = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch", "Tablet"],
    "Fashion": ["T-Shirt", "Jeans", "Sneakers", "Jacket", "Kurta"],
    "Home & Kitchen": ["Mixer Grinder", "Cookware Set", "Bedsheet", "Table Lamp"],
    "Beauty": ["Face Wash", "Perfume", "Lipstick", "Shampoo"],
    "Books": ["Novel", "Self-Help Book", "Comic", "Textbook"],
}

CITIES = ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Multan", "Peshawar", "Quetta"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash on Delivery", "Wallet", "Bank Transfer"]


def generate_raw_data(n=N_ORDERS) -> pd.DataFrame:
    rows = []
    n_customers = n // 3
    start_date = pd.Timestamp("2025-01-01")

    for order_id in range(1, n + 1):
        category = np.random.choice(list(CATEGORIES.keys()))
        product = np.random.choice(CATEGORIES[category])
        customer_id = np.random.randint(1, n_customers + 1)

        price = round(np.random.uniform(5, 500), 2)
        quantity = np.random.randint(1, 6)
        order_date = start_date + pd.Timedelta(days=int(np.random.randint(0, 300)))
        city = np.random.choice(CITIES)
        payment = np.random.choice(PAYMENT_METHODS)
        rating = np.random.choice([1, 2, 3, 4, 5, np.nan], p=[0.03, 0.05, 0.12, 0.30, 0.40, 0.10])

        rows.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "category": category,
            "product": product,
            "price": price,
            "quantity": quantity,
            "city": city,
            "payment_method": payment,
            "rating": rating,
        })

    df = pd.DataFrame(rows)

    # --- Inject real-world messiness on purpose ---
    dirty = df.copy()

    # 1. Duplicate ~2% of rows
    dup_sample = dirty.sample(frac=0.02, random_state=RANDOM_SEED)
    dirty = pd.concat([dirty, dup_sample], ignore_index=True)

    # 2. Null out some prices / cities / payment methods
    for col, frac in [("price", 0.01), ("city", 0.015), ("payment_method", 0.01)]:
        idx = dirty.sample(frac=frac, random_state=RANDOM_SEED).index
        dirty.loc[idx, col] = np.nan

    # 3. Inconsistent casing / whitespace in text columns
    idx = dirty.sample(frac=0.1, random_state=RANDOM_SEED + 1).index
    dirty.loc[idx, "city"] = dirty.loc[idx, "city"].astype(str).str.upper() + "  "

    # 4. A few negative / zero quantities (data entry errors)
    idx = dirty.sample(n=15, random_state=RANDOM_SEED).index
    dirty.loc[idx, "quantity"] = -1

    # 5. order_date stored as string for some rows (mixed types)
    idx = dirty.sample(frac=0.2, random_state=RANDOM_SEED + 2).index
    dirty.loc[idx, "order_date"] = dirty.loc[idx, "order_date"].astype(str)

    return dirty


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    # Normalize text columns: strip whitespace + title case
    for col in ["city", "payment_method", "category", "product"]:
        df[col] = df[col].astype(str).str.strip().str.title()
        df.loc[df[col].isin(["Nan", "None"]), col] = np.nan

    # Parse dates robustly (handles mixed str/Timestamp)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates(subset=["order_id", "customer_id", "product", "order_date"])
    removed_dupes = before - len(df)

    # Fix invalid quantities (negative/zero -> treat as 1, the most common case)
    df.loc[df["quantity"] <= 0, "quantity"] = 1

    # Impute missing price with the median price for that product
    df["price"] = df.groupby("product")["price"].transform(
        lambda s: s.fillna(s.median())
    )
    df["price"] = df["price"].fillna(df["price"].median())

    # Drop rows missing critical fields (city, payment_method) rather than guess
    before = len(df)
    df = df.dropna(subset=["city", "payment_method", "order_date"])
    removed_na = before - len(df)

    # Derived column used by later scripts
    df["revenue"] = (df["price"] * df["quantity"]).round(2)

    df = df.reset_index(drop=True)

    print(f"Removed {removed_dupes} duplicate rows.")
    print(f"Removed {removed_na} rows with missing critical fields.")
    print(f"Final clean dataset: {len(df)} rows, {df['customer_id'].nunique()} unique customers.")

    return df


if __name__ == "__main__":
    raw_df = generate_raw_data()
    raw_path = DATA_DIR / "raw_ecommerce_data.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"Raw (dirty) data saved to: {raw_path}  ({len(raw_df)} rows)")

    clean_df = clean_data(raw_df)
    clean_path = DATA_DIR / "cleaned_ecommerce_data.csv"
    clean_df.to_csv(clean_path, index=False)
    print(f"Cleaned data saved to: {clean_path}")
