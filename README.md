# End-to-End Retail Analytics Pipeline

A professional data engineering and analytics project built on 541,909 real
transactions from a UK-based online retailer.

## Project structure

```
retail\_analytics/
├── run\_pipeline.py          ← run everything in one command
├── requirements.txt
├── data/
│   ├── raw/data.csv         ← place Kaggle dataset here
│   ├── processed/           ← auto-created clean data
│   └── retail.db            ← SQLite database
├── etl/
│   └── etl\_pipeline.py      ← Extract → Transform → Load
├── sql/
│   └── analytics\_queries.py ← 8 business SQL queries
├── analysis/
│   └── rfm\_analysis.py      ← RFM customer segmentation
├── dashboard/
│   └── app.py               ← Power BI interactive dashboard
└── reports/                 ← auto-generated CSV + chart outputs
```

## Quick start

```bash
pip install -r requirements.txt

# place data.csv in data/raw/ then:
python run\_pipeline.py
```

## What the pipeline does

1. **ETL** — cleans 541,909 rows: removes cancellations, nulls, invalid prices/quantities; engineers date features
2. **SQL Analytics** — 8 business queries: monthly revenue, top products, country analysis, hourly patterns
3. **RFM Segmentation** — segments customers into Champions, Loyal, At Risk, Hibernating etc.
4. **Dashboard — interactive Power BI dashboard with revenue trends, RFM segmentation, product and geographic analysis.

## Dataset

Kaggle Online Retail Dataset — 541,909 transactions, 8 columns, 38 countries

## Tech stack

Python · Pandas · SQLite · Plotly · Power BI · Matplotlib



## Dashboard Preview

!\[Dashboard](dashboard%20screenshot.png)

