import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from sqlalchemy import create_engine
import os
import time

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Sales Performance Dashboard",
    layout="wide"
)

# =====================================
# DARK / LIGHT MODE TOGGLE
# =====================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.sidebar:
    st.subheader("Theme")
    theme_toggle = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
    st.session_state.theme = "dark" if theme_toggle else "light"

# =====================================
# THEME CSS
# =====================================
LIGHT_CSS = """
<style>
.stApp { background: linear-gradient(135deg,#f8f9fc,#eef1f7); color:#1f2937; }
h1,h2,h3 { color:#1f2937; }
div[data-testid="metric-container"]{
 background:rgba(255,255,255,0.75); border-radius:12px; padding:12px;
 backdrop-filter:blur(10px); border:1px solid rgba(0,0,0,0.05);
 box-shadow:0 4px 14px rgba(0,0,0,0.08);
 transition:all .25s ease;
}
div[data-testid="metric-container"]:hover{
 transform:translateY(-3px) scale(1.02);
 box-shadow:0 8px 22px rgba(0,0,0,0.14);
}
.element-container:hover{ transform:scale(1.01); transition:.2s; }
</style>
"""

DARK_CSS = """
<style>
.stApp { background: linear-gradient(135deg,#0f2027,#203a43); color:#f9fafb; }
h1,h2,h3 { color:#f9fafb; }
div[data-testid="metric-container"]{
 background:rgba(255,255,255,0.08); border-radius:12px; padding:12px;
 backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.15);
 box-shadow:0 6px 22px rgba(0,0,0,0.5);
 transition:all .25s ease;
}
div[data-testid="metric-container"]:hover{
 transform:translateY(-3px) scale(1.02);
 box-shadow:0 12px 30px rgba(0,0,0,0.8);
}
.element-container:hover{ transform:scale(1.01); transition:.2s; }
</style>
"""

st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# =====================================
# TITLE
# =====================================
st.title("Sales Performance Analysis")

# =====================================
# DATABASE CONNECTION
# =====================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sql", "sales.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM orders_final", engine)

df = load_data()
st.caption(f"{df.shape[0]} records loaded")

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.subheader("Filters")

regions = sorted(df["Region"].dropna().unique())
categories = sorted(df["Category"].dropna().unique())

region_filter = st.sidebar.multiselect("Region", regions, default=regions)
category_filter = st.sidebar.multiselect("Category", categories, default=categories)

filtered_df = df[
    df["Region"].isin(region_filter) &
    df["Category"].isin(category_filter)
]

# =====================================
# ANIMATED KPI COUNTERS
# =====================================
def animated_metric(label, value, prefix="", suffix="", duration=0.8):
    placeholder = st.empty()
    steps = 30
    for i in range(steps + 1):
        current = value * i / steps
        placeholder.metric(label, f"{prefix}{current:,.0f}{suffix}")
        time.sleep(duration / steps)

st.subheader("Key Metrics")

k1, k2, k3, k4 = st.columns(4)

with k1:
    animated_metric("Sales", filtered_df["Sales"].sum(), prefix="$")
with k2:
    animated_metric("Profit", filtered_df["Profit"].sum(), prefix="$")
with k3:
    animated_metric("Quantity", filtered_df["Quantity"].sum())
with k4:
    animated_metric(
        "Return Rate",
        filtered_df["IsReturned"].mean() * 100,
        suffix="%"
    )

# =====================================
# COMPACT CHART GRID
# =====================================
col1, col2 = st.columns(2)

# -------- Bar: State Sales (Tooltip enabled)
with col1:
    st.subheader("Top States by Sales")
    state_sales = (
        filtered_df.groupby("State")["Sales"]
        .sum().sort_values(ascending=False).head(8)
    )

    fig, ax = plt.subplots(figsize=(5,3))
    bars = ax.barh(state_sales.index, state_sales.values, color="#ff7aa2")
    ax.invert_yaxis()
    fig.tight_layout()

    cursor = mplcursors.cursor(bars, hover=True)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(
            f"{sel.target[1]:,.0f}"
        )
    )

    st.pyplot(fig)

# -------- Bar: Category Sales (Tooltip enabled)
with col2:
    st.subheader("Sales by Category")
    category_sales = filtered_df.groupby("Category")["Sales"].sum()

    fig, ax = plt.subplots(figsize=(5,3))
    bars = ax.bar(category_sales.index, category_sales.values, color="#6a82fb")
    fig.tight_layout()

    cursor = mplcursors.cursor(bars, hover=True)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(
            f"{sel.target[1]:,.0f}"
        )
    )

    st.pyplot(fig)

# =====================================
# LINE CHART (Tooltip enabled)
# =====================================
st.subheader("Sales Trend Over Time")

trend = filtered_df.groupby("Parsed_Order_Date")["Sales"].sum().reset_index()

fig, ax = plt.subplots(figsize=(8,3))
line, = ax.plot(trend["Parsed_Order_Date"], trend["Sales"], color="#6a82fb", linewidth=2)
fig.tight_layout()

cursor = mplcursors.cursor(line, hover=True)
cursor.connect(
    "add",
    lambda sel: sel.annotation.set_text(
        f"{sel.target[1]:,.0f}"
    )
)

st.pyplot(fig)

# =====================================
# PIE + TABLE (NO OVERLAP)
# =====================================
c3, c4 = st.columns([1,1.2])

with c3:
    st.subheader("Sales by Region")
    region_sales = filtered_df.groupby("Region")["Sales"].sum()

    fig, ax = plt.subplots(figsize=(4,4))
    wedges, _, _ = ax.pie(
        region_sales,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.75
    )

    ax.legend(
        wedges,
        region_sales.index,
        loc="center left",
        bbox_to_anchor=(1,0.5),
        fontsize=9
    )

    fig.tight_layout()
    st.pyplot(fig)

with c4:
    st.subheader("Top Products")
    top_products = (
        filtered_df.groupby("Product Name")["Sales"]
        .sum().sort_values(ascending=False).head(8)
    )
    st.dataframe(top_products.reset_index(), height=260)

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("Sales Performance Dashboard • Streamlit • SQLite • Pandas")
