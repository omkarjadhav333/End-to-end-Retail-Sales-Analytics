"""
etl_pipeline.py
Extract → Transform → Load pipeline for Online Retail Dataset.
Run: python etl/etl_pipeline.py
"""
from __future__ import annotations

import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT     = Path(__file__).parent.parent
RAW_DIR  = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
DB_PATH  = ROOT / "data" / "retail.db"
PROC_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ETL")


def extract() -> pd.DataFrame:
    log.info("EXTRACT — reading raw file...")
    path = RAW_DIR / "data.csv"
    if not path.exists():
        log.critical("File not found: %s", path)
        sys.exit(1)
    df = pd.read_csv(path, encoding="latin-1")
    log.info("  Raw rows: %d  Columns: %s", len(df), list(df.columns))
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("TRANSFORM — cleaning data...")
    before = len(df)

    # drop rows with missing CustomerID or Description
    df.dropna(subset=["CustomerID", "Description"], inplace=True)
    log.info("  Dropped %d rows with missing CustomerID/Description", before - len(df))

    # remove cancellations (InvoiceNo starting with C)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    log.info("  Removed cancellations — remaining: %d", len(df))

    # remove invalid quantities and prices
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    log.info("  Removed invalid qty/price — remaining: %d", len(df))

    # fix data types
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["CustomerID"]  = df["CustomerID"].astype(int).astype(str)
    df["UnitPrice"]   = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["Quantity"]    = pd.to_numeric(df["Quantity"],  errors="coerce")
    df.dropna(subset=["InvoiceDate"], inplace=True)

    # engineer new columns
    df["TotalPrice"]  = (df["Quantity"] * df["UnitPrice"]).round(2)
    df["Year"]        = df["InvoiceDate"].dt.year
    df["Month"]       = df["InvoiceDate"].dt.month
    df["Quarter"]     = df["InvoiceDate"].dt.quarter
    df["YearMonth"]   = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["DayOfWeek"]   = df["InvoiceDate"].dt.day_name()
    df["Hour"]        = df["InvoiceDate"].dt.hour

    # clean description
    df["Description"] = df["Description"].str.strip().str.title()
    df["Country"]     = df["Country"].str.strip()

    log.info("  Final clean rows: %d", len(df))
    return df


def load(df: pd.DataFrame) -> None:
    log.info("LOAD — writing to SQLite and CSV...")

    df.to_csv(PROC_DIR / "retail_clean.csv", index=False)
    log.info("  Saved: data/processed/retail_clean.csv")

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("transactions", conn, if_exists="replace", index=False)
    log.info("  Loaded %d rows into SQLite table: transactions", len(df))
    conn.close()


def validate() -> None:
    log.info("VALIDATE — running checks...")
    conn = sqlite3.connect(DB_PATH)
    checks = {
        "Total transactions":    "SELECT COUNT(*) FROM transactions",
        "Unique customers":      "SELECT COUNT(DISTINCT CustomerID) FROM transactions",
        "Unique products":       "SELECT COUNT(DISTINCT StockCode) FROM transactions",
        "Unique countries":      "SELECT COUNT(DISTINCT Country) FROM transactions",
        "Total revenue":         "SELECT ROUND(SUM(TotalPrice),2) FROM transactions",
        "Date range start":      "SELECT MIN(InvoiceDate) FROM transactions",
        "Date range end":        "SELECT MAX(InvoiceDate) FROM transactions",
    }
    for label, query in checks.items():
        val = conn.execute(query).fetchone()[0]
        log.info("  %-28s %s", label, val)
    conn.close()


def main():
    print("=" * 48)
    print("  Retail Analytics — ETL Pipeline")
    print("=" * 48)
    start = datetime.now()
    raw   = extract()
    clean = transform(raw)
    load(clean)
    validate()
    elapsed = (datetime.now() - start).total_seconds()
    log.info("Pipeline completed in %.2fs ✓", elapsed)


if __name__ == "__main__":
    main()
