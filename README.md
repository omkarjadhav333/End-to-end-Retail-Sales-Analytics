# End-to-End Retail Analytics Pipeline

A professional data engineering and analytics project built on 541,909 real
transactions from a UK-based online retailer.

## Project structure
```
retail_analytics/
├── run_pipeline.py          ← run everything in one command
├── requirements.txt
├── data/
│   ├── raw/data.csv         ← place Kaggle dataset here
│   ├── processed/           ← auto-created clean data
│   └── retail.db            ← SQLite database
├── etl/
│   └── etl_pipeline.py      ← Extract → Transform → Load
├── sql/
│   └── analytics_queries.py ← 8 business SQL queries
├── analysis/
│   └── rfm_analysis.py      ← RFM customer segmentation
├── dashboard/
│   └── app.py               ← Streamlit interactive dashboard
└── reports/                 ← auto-generated CSV + chart outputs
```

## Quick start
```bash
pip install -r requirements.txt

# place data.csv in data/raw/ then:
python run_pipeline.py
```

## What the pipeline does
1. **ETL** — cleans 541,909 rows: removes cancellations, nulls, invalid prices/quantities; engineers date features
2. **SQL Analytics** — 8 business queries: monthly revenue, top products, country analysis, hourly patterns
3. **RFM Segmentation** — segments customers into Champions, Loyal, At Risk, Hibernating etc.
4. **Dashboard** — interactive Streamlit app with filters for year and country

## Dataset
Kaggle Online Retail Dataset — 541,909 transactions, 8 columns, 38 countries

## Tech stack
Python · Pandas · SQLite · Plotly · Streamlit · Matplotlib
