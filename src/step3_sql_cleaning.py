from sqlalchemy import create_engine, text
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sql", "sales.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_cleaned;"))
    conn.execute(text("""
        CREATE TABLE orders_cleaned AS
        SELECT * FROM orders;
    """))
    conn.commit()

print("STEP 3.1 DONE: orders_cleaned table created")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_tmp;"))

    conn.execute(text("""
        CREATE TABLE orders_tmp AS
        SELECT
            "Row ID",
            "Order Date",
            "Order ID",
            "Ship Date",
            "Ship Mode",
            "ShipModeCorrected",
            "Customer ID",
            "Customer Name",
            "Segment",
            "Country",
            "City",
            "State",
            "Postal Code",
            "Region",
            "Product ID",
            "Category",
            "Sub-Category",
            "Product Name",
            "Sales",
            "Quantity",
            "Discount",
            "Profit"
        FROM orders_cleaned;
    """))

    conn.execute(text("DROP TABLE orders_cleaned;"))
    conn.execute(text("ALTER TABLE orders_tmp RENAME TO orders_cleaned;"))
    conn.commit()

print("STEP 3.2 DONE: Junk column removed")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_typed;"))

    conn.execute(text("""
        CREATE TABLE orders_typed AS
        SELECT
            "Row ID",
            "Order Date",
            "Order ID",
            "Ship Date",
            "Ship Mode",
            "ShipModeCorrected",
            "Customer ID",
            "Customer Name",
            "Segment",
            "Country",
            "City",
            "State",
            "Postal Code",
            "Region",
            "Product ID",
            "Category",
            "Sub-Category",
            "Product Name",
            CAST("Sales" AS REAL) AS Sales,
            CAST("Quantity" AS INTEGER) AS Quantity,
            CAST("Discount" AS REAL) AS Discount,
            CAST("Profit" AS REAL) AS Profit
        FROM orders_cleaned;
    """))

    conn.execute(text("DROP TABLE orders_cleaned;"))
    conn.execute(text("ALTER TABLE orders_typed RENAME TO orders_cleaned;"))
    conn.commit()

print("STEP 3.3 DONE: Numeric columns enforced")
with engine.connect() as conn:
    medians = conn.execute(text("""
        SELECT
            (SELECT Sales FROM orders_cleaned ORDER BY Sales LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM orders_cleaned)) AS m_sales,
            (SELECT Quantity FROM orders_cleaned ORDER BY Quantity LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM orders_cleaned)) AS m_quantity,
            (SELECT Profit FROM orders_cleaned ORDER BY Profit LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM orders_cleaned)) AS m_profit
    """)).fetchone()

    conn.execute(text("""
        UPDATE orders_cleaned
        SET
            Sales = COALESCE(Sales, :ms),
            Quantity = COALESCE(Quantity, :mq),
            Discount = COALESCE(Discount, 0),
            Profit = COALESCE(Profit, :mp);
    """), {"ms": medians[0], "mq": medians[1], "mp": medians[2]})

    conn.commit()

print("STEP 3.4 DONE: Missing values handled")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS orders_dedup;"))

    conn.execute(text("""
        CREATE TABLE orders_dedup AS
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY "Order ID", "Product ID", Quantity
                       ORDER BY "Row ID"
                   ) rn
            FROM orders_cleaned
        )
        WHERE rn = 1;
    """))

    conn.execute(text("DROP TABLE orders_cleaned;"))
    conn.execute(text("ALTER TABLE orders_dedup RENAME TO orders_cleaned;"))
    conn.commit()

print("STEP 3.5 DONE: Duplicates removed")
with engine.connect() as conn:
    conn.execute(text("""
        UPDATE orders_cleaned
        SET
            "City" = UPPER(TRIM("City")),
            "State" = UPPER(TRIM("State")),
            "Region" = UPPER(TRIM("Region")),
            "Category" = UPPER(TRIM("Category")),
            "Sub-Category" = UPPER(TRIM("Sub-Category")),
            "Ship Mode" = UPPER(TRIM("Ship Mode")),
            "Segment" = UPPER(TRIM("Segment"));
    """))
    conn.commit()

print("STEP 3.6 DONE: Text standardized")
