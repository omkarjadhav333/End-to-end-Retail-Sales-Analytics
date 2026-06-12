"""
app.py — Retail Analytics Dashboard (Online Retail Dataset)
Run: streamlit run dashboard/app.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT    = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "retail.db"

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
)

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df

try:
    df_all = load_data()
except Exception as e:
    st.error(f"Database not found. Run `python etl/etl_pipeline.py` first.\n{e}")
    st.stop()

# ── sidebar filters ────────────────────────────────────────────────────
st.sidebar.title("🔧 Filters")
years     = sorted(df_all["Year"].dropna().unique().astype(int).tolist())
sel_years = st.sidebar.multiselect("Year", years, default=years)
countries = sorted(df_all["Country"].dropna().unique().tolist())
sel_ctry  = st.sidebar.multiselect("Country", countries, default=["United Kingdom"])

df = df_all[
    df_all["Year"].isin(sel_years) &
    df_all["Country"].isin(sel_ctry)
].copy()

# ── header ─────────────────────────────────────────────────────────────
st.title("🛒 Retail Analytics Dashboard")
st.caption("Online Retail Dataset — 541,909 transactions | UK-based retailer")
st.markdown("---")

# ── KPIs ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Total Revenue",   f"£{df['TotalPrice'].sum()/1e6:.2f}M")
k2.metric("🛍️ Total Orders",   f"{df['InvoiceNo'].nunique():,}")
k3.metric("👥 Customers",       f"{df['CustomerID'].nunique():,}")
k4.metric("📦 Products",        f"{df['StockCode'].nunique():,}")
k5.metric("🌍 Countries",       f"{df['Country'].nunique():,}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Revenue Trends", "📦 Product Analysis",
    "👥 Customer Insights", "🗺️ Geographic Analysis"
])

# ═══════════════════════════════════════
# TAB 1 — REVENUE TRENDS
# ═══════════════════════════════════════
with tab1:
    monthly = (df.groupby("YearMonth")
               .agg(revenue=("TotalPrice","sum"),
                    orders=("InvoiceNo","nunique"),
                    customers=("CustomerID","nunique"))
               .reset_index().sort_values("YearMonth"))

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(monthly, x="YearMonth", y="revenue",
                      title="Monthly Revenue Trend",
                      labels={"revenue":"Revenue (£)","YearMonth":"Month"})
        fig.update_traces(line_color="#E8593C", line_width=2)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(monthly, x="YearMonth", y="orders",
                      title="Monthly Order Volume",
                      labels={"orders":"Orders","YearMonth":"Month"},
                      color_discrete_sequence=["#4C72B0"])
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)

    # day of week
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = df.groupby("DayOfWeek").agg(
        revenue=("TotalPrice","sum"), orders=("InvoiceNo","nunique")).reset_index()
    dow["DayOfWeek"] = pd.Categorical(dow["DayOfWeek"], categories=dow_order, ordered=True)
    dow.sort_values("DayOfWeek", inplace=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(dow, x="DayOfWeek", y="revenue",
                      title="Revenue by Day of Week",
                      color_discrete_sequence=["#2ecc71"])
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        hour = df.groupby("Hour").agg(orders=("InvoiceNo","nunique")).reset_index()
        fig4 = px.bar(hour, x="Hour", y="orders",
                      title="Orders by Hour of Day",
                      color_discrete_sequence=["#9b59b6"])
        st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════
# TAB 2 — PRODUCT ANALYSIS
# ═══════════════════════════════════════
with tab2:
    top10 = (df.groupby(["StockCode","Description"])
             .agg(revenue=("TotalPrice","sum"), units=("Quantity","sum"))
             .reset_index().nlargest(10,"revenue"))

    fig = px.bar(top10, x="revenue", y="Description", orientation="h",
                 title="Top 10 Products by Revenue",
                 color_discrete_sequence=["#E8593C"],
                 labels={"revenue":"Revenue (£)","Description":""})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        top10u = (df.groupby("Description")["Quantity"].sum()
                  .nlargest(10).reset_index())
        fig2 = px.bar(top10u, x="Quantity", y="Description", orientation="h",
                      title="Top 10 Products by Units Sold",
                      color_discrete_sequence=["#4C72B0"],
                      labels={"Description":""})
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        price_dist = df.groupby("Description")["UnitPrice"].mean().reset_index()
        fig3 = px.histogram(price_dist, x="UnitPrice", nbins=50,
                            title="Product Price Distribution",
                            labels={"UnitPrice":"Unit Price (£)"},
                            color_discrete_sequence=["#2ecc71"])
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════
# TAB 3 — CUSTOMER INSIGHTS
# ═══════════════════════════════════════
with tab3:
    cust = (df.groupby("CustomerID")
            .agg(total_spent=("TotalPrice","sum"),
                 total_orders=("InvoiceNo","nunique"),
                 total_items=("Quantity","sum"))
            .reset_index())

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(cust, x="total_spent", nbins=50,
                           title="Customer Spend Distribution",
                           labels={"total_spent":"Total Spend (£)"},
                           color_discrete_sequence=["#E8593C"])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.histogram(cust, x="total_orders", nbins=30,
                            title="Order Frequency Distribution",
                            labels={"total_orders":"Number of Orders"},
                            color_discrete_sequence=["#4C72B0"])
        st.plotly_chart(fig2, use_container_width=True)

    # RFM segments
    rfm_path = ROOT / "reports" / "rfm_segments.csv"
    if rfm_path.exists():
        st.subheader("RFM Customer Segments")
        rfm = pd.read_csv(rfm_path)
        col3, col4 = st.columns(2)
        with col3:
            seg_c = rfm["rfm_segment"].value_counts().reset_index()
            seg_c.columns = ["Segment","Customers"]
            fig3 = px.pie(seg_c, values="Customers", names="Segment",
                          title="Customers by RFM Segment", hole=0.4)
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            seg_r = rfm.groupby("rfm_segment")["monetary"].sum().reset_index()
            fig4 = px.bar(seg_r.sort_values("monetary"), x="monetary", y="rfm_segment",
                          orientation="h", title="Revenue by RFM Segment",
                          color_discrete_sequence=["#9b59b6"],
                          labels={"monetary":"Revenue (£)","rfm_segment":""})
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Run `python analysis/rfm_analysis.py` to see RFM segments.")

# ═══════════════════════════════════════
# TAB 4 — GEOGRAPHIC ANALYSIS
# ═══════════════════════════════════════
with tab4:
    country = (df_all.groupby("Country")
               .agg(revenue=("TotalPrice","sum"),
                    customers=("CustomerID","nunique"),
                    orders=("InvoiceNo","nunique"))
               .reset_index().nlargest(15,"revenue"))

    fig = px.bar(country, x="revenue", y="Country", orientation="h",
                 title="Top 15 Countries by Revenue",
                 color_discrete_sequence=["#E8593C"],
                 labels={"revenue":"Revenue (£)","Country":""})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.pie(country.head(8), values="revenue", names="Country",
                      title="Revenue Share by Country", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.bar(country, x="customers", y="Country", orientation="h",
                      title="Customers by Country",
                      color_discrete_sequence=["#4C72B0"],
                      labels={"customers":"Customers","Country":""})
        st.plotly_chart(fig3, use_container_width=True)
