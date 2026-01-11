from sqlalchemy import create_engine, text
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sql", "sales.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

print("Connected to DB:", DB_PATH)

# STEP 4.2 — Orders + Returns
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_with_returns;"))

    conn.execute(text("""
        CREATE TABLE orders_with_returns AS
        SELECT
            o.*,
            CASE
                WHEN r.Returned = 'Yes' THEN 1
                ELSE 0
            END AS IsReturned
        FROM orders_cleaned o
        LEFT JOIN returns r
            ON o."Order ID" = r."Order ID";
    """))
    conn.commit()

print("STEP 4.2 DONE: orders_with_returns created")

# STEP 4.3 — Add SalesRep
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_enriched;"))

    conn.execute(text("""
        CREATE TABLE orders_enriched AS
        SELECT
            owr.*,
            p.Person AS SalesRep
        FROM orders_with_returns owr
        LEFT JOIN people p
            ON owr.Region = p.Region;
    """))
    conn.commit()

print("STEP 4.3 DONE: orders_enriched created")

# STEP 4.4 — Derived features
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_final;"))

    conn.execute(text("""
        CREATE TABLE orders_final AS
        SELECT
            oe.*,

            date(
                substr("Order Date", 7, 4) || '-' ||
                substr("Order Date", 1, 2) || '-' ||
                substr("Order Date", 4, 2)
            ) AS Parsed_Order_Date,

            CAST(strftime('%Y',
                substr("Order Date", 7, 4) || '-' ||
                substr("Order Date", 1, 2) || '-' ||
                substr("Order Date", 4, 2)
            ) AS INTEGER) AS OrderYear,

            CAST(strftime('%m',
                substr("Order Date", 7, 4) || '-' ||
                substr("Order Date", 1, 2) || '-' ||
                substr("Order Date", 4, 2)
            ) AS INTEGER) AS OrderMonth,

            ((CAST(strftime('%m',
                substr("Order Date", 7, 4) || '-' ||
                substr("Order Date", 1, 2) || '-' ||
                substr("Order Date", 4, 2)
            ) AS INTEGER) - 1) / 3 + 1) AS OrderQuarter,

            CASE
                WHEN Sales = 0 THEN 0
                ELSE Profit / Sales
            END AS ProfitMargin

        FROM orders_enriched oe;
    """))
    conn.commit()

print("STEP 4.4 DONE: orders_final created")
print("STEP 4 COMPLETE")
