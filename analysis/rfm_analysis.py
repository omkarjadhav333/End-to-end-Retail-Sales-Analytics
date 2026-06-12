"""
rfm_analysis.py
RFM (Recency, Frequency, Monetary) customer segmentation.
Run: python analysis/rfm_analysis.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

ROOT    = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "retail.db"
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(exist_ok=True)


def compute_rfm() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            CustomerID,
            Country,
            MAX(InvoiceDate)              AS last_purchase,
            COUNT(DISTINCT InvoiceNo)     AS frequency,
            ROUND(SUM(TotalPrice), 2)     AS monetary
        FROM transactions
        GROUP BY CustomerID
    """, conn)
    conn.close()

    snapshot = pd.Timestamp("2011-12-31")
    df["last_purchase"] = pd.to_datetime(df["last_purchase"])
    df["recency"]       = (snapshot - df["last_purchase"]).dt.days

    # score 1-5
    df["R"] = pd.qcut(df["recency"],   5, labels=[5,4,3,2,1]).astype(int)
    df["F"] = pd.qcut(df["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    df["M"] = pd.qcut(df["monetary"],  5, labels=[1,2,3,4,5]).astype(int)
    df["RFM_Score"] = df["R"] + df["F"] + df["M"]

    def segment(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4 and m >= 4:   return "Champions"
        elif r >= 3 and f >= 3:             return "Loyal Customers"
        elif r >= 4 and f <= 2:             return "New Customers"
        elif r >= 3 and m >= 3:             return "Potential Loyalists"
        elif r <= 2 and f >= 3:             return "At Risk"
        elif r == 1 and f >= 4:             return "Cannot Lose Them"
        elif r <= 2 and f <= 2:             return "Hibernating"
        else:                               return "Needs Attention"

    df["rfm_segment"] = df.apply(segment, axis=1)
    return df


def plot_rfm(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("RFM Customer Segmentation — Online Retail", fontsize=14)

    seg_counts = df["rfm_segment"].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(seg_counts)))
    axes[0].barh(seg_counts.index, seg_counts.values, color=colors, edgecolor="none")
    axes[0].set_title("Customers per Segment")
    axes[0].set_xlabel("Count")

    seg_rev = df.groupby("rfm_segment")["monetary"].sum().sort_values()
    axes[1].barh(seg_rev.index, seg_rev.values / 1e3, color="#E8593C", edgecolor="none")
    axes[1].set_title("Revenue by Segment (£K)")
    axes[1].set_xlabel("Revenue (£ Thousands)")

    axes[2].hist(df["RFM_Score"], bins=12, color="#4C72B0", edgecolor="white")
    axes[2].set_title("RFM Score Distribution")
    axes[2].set_xlabel("RFM Score")
    axes[2].set_ylabel("Customers")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "rfm_analysis.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Chart saved: reports/rfm_analysis.png")


def main():
    print("=" * 48)
    print("  Retail Analytics — RFM Segmentation")
    print("=" * 48 + "\n")

    df = compute_rfm()

    summary = df.groupby("rfm_segment").agg(
        customers    = ("CustomerID", "count"),
        avg_recency  = ("recency",    "mean"),
        avg_frequency= ("frequency",  "mean"),
        avg_monetary = ("monetary",   "mean"),
        total_revenue= ("monetary",   "sum"),
    ).round(2).sort_values("total_revenue", ascending=False)

    print(summary.to_string())

    df.to_csv(OUT_DIR / "rfm_segments.csv", index=False)
    summary.to_csv(OUT_DIR / "rfm_summary.csv")
    plot_rfm(df)

    print(f"\n  Champions      : {(df['rfm_segment']=='Champions').sum()} customers")
    print(f"  At Risk        : {(df['rfm_segment']=='At Risk').sum()} customers")
    print(f"  Cannot Lose    : {(df['rfm_segment']=='Cannot Lose Them').sum()} customers")
    print("\n  Saved: reports/rfm_segments.csv")


if __name__ == "__main__":
    main()
