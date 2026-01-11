import pandas as pd
from sqlalchemy import create_engine
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "Sample - Superstore - Training.xlsx")
DB_PATH = os.path.join(BASE_DIR, "sql", "sales.db")

print("Excel path:", DATA_PATH)
print("Database path:", DB_PATH)

# Load Excel sheets
xls = pd.ExcelFile(DATA_PATH)

orders_df = pd.read_excel(xls, sheet_name="Orders")
returns_df = pd.read_excel(xls, sheet_name="Returns")
people_df = pd.read_excel(xls, sheet_name="People")

print("Orders shape:", orders_df.shape)
print("Returns shape:", returns_df.shape)
print("People shape:", people_df.shape)

# Create database
engine = create_engine(f"sqlite:///{DB_PATH}")

# Load to SQL
orders_df.to_sql("orders", engine, if_exists="replace", index=False)
returns_df.to_sql("returns", engine, if_exists="replace", index=False)
people_df.to_sql("people", engine, if_exists="replace", index=False)

print("STEP 2 COMPLETE: Data loaded into SQLite database")
