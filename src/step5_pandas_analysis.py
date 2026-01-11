import pandas as pd
from sqlalchemy import create_engine
import os

# -----------------------------
# Database connection
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sql", "sales.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

print("Connected to database:", DB_PATH)

# -----------------------------
# Load final table into Pandas
# -----------------------------
df = pd.read_sql("SELECT * FROM orders_final", engine)

print("\nData loaded into Pandas")
print("Shape:", df.shape)
print(df.head())

# =====================================================
# 1. SALES PERFORMANCE METRICS
# =====================================================
print("\n--- SALES PERFORMANCE METRICS ---")

total_sales = df["Sales"].sum()
total_quantity = df["Quantity"].sum()
total_profit = df["Profit"].sum()
avg_sales_per_order = df.groupby("Order ID")["Sales"].sum().mean()
profit_margin = total_profit / total_sales if total_sales != 0 else 0

print("Total Sales:", round(total_sales, 2))
print("Total Quantity Sold:", total_quantity)
print("Total Profit:", round(total_profit, 2))
print("Average Sales per Order:", round(avg_sales_per_order, 2))
print("Overall Profit Margin:", round(profit_margin, 4))

# =====================================================
# 2. TOP PERFORMANCE ANALYSIS
# =====================================================
print("\n--- TOP PRODUCTS BY SALES ---")
top_products_sales = (
    df.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print(top_products_sales)

print("\n--- TOP PRODUCTS BY QUANTITY ---")
top_products_qty = (
    df.groupby("Product Name")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print(top_products_qty)

print("\n--- TOP CUSTOMERS BY SALES ---")
top_customers = (
    df.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print(top_customers)

# =====================================================
# 3. GEOGRAPHICAL ANALYSIS
# =====================================================
print("\n--- SALES & PROFIT BY REGION ---")
region_perf = df.groupby("Region")[["Sales", "Profit"]].sum()
print(region_perf)

# =====================================================
# 4. CATEGORY ANALYSIS
# =====================================================
print("\n--- CATEGORY PERFORMANCE ---")
category_perf = df.groupby("Category")[["Sales", "Quantity"]].sum()
print(category_perf)

print("\n--- SUB-CATEGORY PERFORMANCE (Top 5 by Sales) ---")
subcategory_perf = (
    df.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print(subcategory_perf)

# =====================================================
# 5. SALES REPRESENTATIVE PERFORMANCE
# =====================================================
print("\n--- SALES REP PERFORMANCE ---")
sales_rep_perf = df.groupby("SalesRep")[["Sales", "Profit"]].sum()
print(sales_rep_perf)

# =====================================================
# 6. RETURN ANALYSIS
# =====================================================
print("\n--- RETURN ANALYSIS ---")
total_orders = df["Order ID"].nunique()
returned_orders = df[df["IsReturned"] == 1]["Order ID"].nunique()
return_rate = returned_orders / total_orders

print("Total Orders:", total_orders)
print("Returned Orders:", returned_orders)
print("Return Rate:", round(return_rate, 4))

print("\n--- HIGH RETURN PRODUCTS (Top 5) ---")
product_returns = (
    df.groupby("Product Name")["IsReturned"]
    .mean()
    .sort_values(ascending=False)
    .head(5)
)
print(product_returns)

# =====================================================
# END
# =====================================================
print("\nSTEP 5 COMPLETE: Pandas analysis finished successfully")
