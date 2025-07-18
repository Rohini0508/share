# transform/transform_to_sql.py

from pymongo import MongoClient
import pyodbc
from datetime import datetime
from config.settings import MONGO_URI, SQL_CONFIG

def transform_and_load():
    client = MongoClient(MONGO_URI)
    raw_data = client["SharePointDB"]["CustomerRaw"].find()

    conn = pyodbc.connect(
        f"DRIVER={{{SQL_CONFIG['DRIVER']}}};"
        f"SERVER={SQL_CONFIG['SERVER']};"
        f"DATABASE={SQL_CONFIG['DATABASE']};"
        f"UID={SQL_CONFIG['USERNAME']};"
        f"PWD={SQL_CONFIG['PASSWORD']}"
    )
    cursor = conn.cursor()

    # Create DimCustomer
    cursor.execute("""
        IF OBJECT_ID('DimCustomer', 'U') IS NULL
        CREATE TABLE DimCustomer (
            customer_key INT IDENTITY(1,1) PRIMARY KEY,
            source_id INT,
            name NVARCHAR(100),
            email NVARCHAR(100)
        )
    """)
    
    # Create FactCustomerActivity
    cursor.execute("""
        IF OBJECT_ID('FactCustomerActivity', 'U') IS NULL
        CREATE TABLE FactCustomerActivity (
            fact_id INT IDENTITY(1,1) PRIMARY KEY,
            customer_key INT,
            activity_type NVARCHAR(50),
            signup_date DATE,
            is_active BIT
        )
    """)
    conn.commit()

    for doc in raw_data:
        source_id = doc.get("id")
        name = doc.get("name")
        email = doc.get("email")
        signup_date = doc.get("signup_date", datetime.today().strftime('%Y-%m-%d'))
        is_active = 1 if doc.get("is_active", True) else 0

        # Insert into DimCustomer
        cursor.execute("""
            INSERT INTO DimCustomer (source_id, name, email)
            VALUES (?, ?, ?)
        """, (source_id, name, email))
        conn.commit()

        # Get current customer_key
        cursor.execute("SELECT IDENT_CURRENT('DimCustomer')")
        customer_key = int(cursor.fetchone()[0])

        # Insert into FactCustomerActivity
        cursor.execute("""
            INSERT INTO FactCustomerActivity (customer_key, activity_type, signup_date, is_active)
            VALUES (?, ?, ?, ?)
        """, (customer_key, "signup", signup_date, is_active))
        conn.commit()

    conn.close()
    print("✅ Data transformed and loaded into SQL Server.")
