"""
analytics_queries.py
Business SQL queries on the Online Retail dataset.
Run: python sql/analytics_queries.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

ROOT    = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "retail.db"
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(exist_ok=True)


def run(conn, label, query):
    df = pd.read_sql_query(query, conn)
    df.to_csv(OUT_DIR / f"{label}.csv", index=False)
    print(f"  ✓  {label:<35} {len(df)} rows")
    return df


def main():
    print("=" * 50)
    print("  Retail Analytics — SQL Queries")
    print("=" * 50 + "\n")

    conn = sqlite3.connect(DB_PATH)

    # 1 — Monthly revenue trend
    run(conn, "monthly_revenue", """
        SELECT YearMonth, Year, Month,
               ROUND(SUM(TotalPrice),2)       AS revenue,
               COUNT(DISTINCT InvoiceNo)      AS orders,
               COUNT(DISTINCT CustomerID)     AS customers
        FROM transactions
        GROUP BY YearMonth
        ORDER BY YearMonth
    """)

    # 2 — Revenue by country (top 10)
    run(conn, "revenue_by_country", """
        SELECT Country,
               ROUND(SUM(TotalPrice),2)       AS revenue,
               COUNT(DISTINCT CustomerID)     AS customers,
               COUNT(DISTINCT InvoiceNo)      AS orders
        FROM transactions
        GROUP BY Country
        ORDER BY revenue DESC
        LIMIT 10
    """)

    # 3 — Top 10 products by revenue
    run(conn, "top_products", """
        SELECT StockCode, Description,
               ROUND(SUM(TotalPrice),2)       AS revenue,
               SUM(Quantity)                  AS units_sold,
               COUNT(DISTINCT InvoiceNo)      AS orders
        FROM transactions
        GROUP BY StockCode, Description
        ORDER BY revenue DESC
        LIMIT 10
    """)

    # 4 — Revenue by day of week
    run(conn, "revenue_by_day", """
        SELECT DayOfWeek,
               COUNT(DISTINCT InvoiceNo)      AS orders,
               ROUND(SUM(TotalPrice),2)       AS revenue,
               ROUND(AVG(TotalPrice),2)       AS avg_order_value
        FROM transactions
        GROUP BY DayOfWeek
        ORDER BY revenue DESC
    """)

    # 5 — Revenue by hour
    run(conn, "revenue_by_hour", """
        SELECT Hour,
               COUNT(DISTINCT InvoiceNo)      AS orders,
               ROUND(SUM(TotalPrice),2)       AS revenue
        FROM transactions
        GROUP BY Hour
        ORDER BY Hour
    """)

    # 6 — Monthly unique customers
    run(conn, "monthly_customers", """
        SELECT YearMonth,
               COUNT(DISTINCT CustomerID)     AS unique_customers,
               COUNT(DISTINCT InvoiceNo)      AS orders,
               ROUND(SUM(TotalPrice)/COUNT(DISTINCT CustomerID),2) AS revenue_per_customer
        FROM transactions
        GROUP BY YearMonth
        ORDER BY YearMonth
    """)

    # 7 — Top customers
    run(conn, "top_customers", """
        SELECT CustomerID,
               Country,
               ROUND(SUM(TotalPrice),2)       AS total_spent,
               COUNT(DISTINCT InvoiceNo)      AS total_orders,
               ROUND(AVG(TotalPrice),2)       AS avg_order_value
        FROM transactions
        GROUP BY CustomerID, Country
        ORDER BY total_spent DESC
        LIMIT 20
    """)

    # 8 — Quarterly revenue
    run(conn, "quarterly_revenue", """
        SELECT Year, Quarter,
               ROUND(SUM(TotalPrice),2)       AS revenue,
               COUNT(DISTINCT InvoiceNo)      AS orders
        FROM transactions
        GROUP BY Year, Quarter
        ORDER BY Year, Quarter
    """)

    conn.close()
    print(f"\n  All reports saved to reports/")


if __name__ == "__main__":
    main()
