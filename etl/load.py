# etl/load.py

import pyodbc
from config.settings import SQL_CONFIG

def create_projects_table_if_not_exists(cursor):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Projects')
    BEGIN
        CREATE TABLE Projects (
            project_name NVARCHAR(255),
            status NVARCHAR(100),
            project_manager NVARCHAR(100),
            start_date DATE,
            end_date DATE,
            budget DECIMAL(18,2),
            department NVARCHAR(100)
        )
    END
    """)

def load_data(df):
    conn_str = (
        f"DRIVER={{{SQL_CONFIG['DRIVER']}}};"
        f"SERVER={SQL_CONFIG['SERVER']};"
        f"DATABASE={SQL_CONFIG['DATABASE']};"
        f"UID={SQL_CONFIG['USERNAME']};"
        f"PWD={SQL_CONFIG['PASSWORD']}"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Create table if not exists
    create_projects_table_if_not_exists(cursor)

    # Ensure row is passed as a tuple
    for _, row in df.iterrows():
        values = (
            str(row['project_name']),
            str(row['status']),
            str(row['project_manager']),
            row['start_date'],
            row['end_date'],
            float(row['budget']),
            str(row['department'])
        )
        cursor.execute("""
            INSERT INTO Projects (project_name, status, project_manager, start_date, end_date, budget, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, values)

    conn.commit()
    conn.close()
