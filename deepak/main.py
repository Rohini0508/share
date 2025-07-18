import io, json, os
import pandas as pd
from configparser import ConfigParser
from sqlalchemy import create_engine, text
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.files.file import File

# Load config
config = ConfigParser()
config.read('config.ini')

# SharePoint config
sp_user = config['sharepoint']['username']
sp_pass = config['sharepoint']['password']
sp_url = config['sharepoint']['site_url']
sp_path = config['sharepoint']['folder_path']

# SQL Server config
db_user = config['sqlserver']['username']
db_pass = config['sqlserver']['password']
db_driver = config['sqlserver']['driver']
db_name = config['sqlserver']['database']
db_server = config['sqlserver']['server']

# SQLAlchemy connection string
conn_str = (
    f"mssql+pyodbc://{db_user}:{db_pass}@{db_server}/{db_name}"
    f"?driver={db_driver.replace(' ', '+')}"
)
engine = create_engine(conn_str)

# Define Primary Keys
primary_keys = {
    "sales_fact": "sale_id",
    "product_dimension": "product_id",
    "store_dimension": "store_id",
    "time_dimension": "date_id",
    "sales_dimensions": "supplier_id",
    "region_dimension": "region_id",
    "promotion_dimension": "promotion_id"
}

# Define Foreign Keys
foreign_keys = {
    "sales_fact": [
        ("product_id", "product_dimension", "product_id"),
        ("store_id", "store_dimension", "store_id"),
        ("date_id", "time_dimension", "date_id")
    ],
    "sales_dimensions": [
        ("region_id", "region_dimension", "region_id"),
        ("promotion_id", "promotion_dimension", "promotion_id")
    ],
    "store_dimension": [
        ("region_id", "region_dimension", "region_id")
    ]
}

# Connect to SharePoint
ctx_auth = AuthenticationContext(sp_url)
if not ctx_auth.acquire_token_for_user(sp_user, sp_pass):
    raise Exception(" SharePoint authentication failed")

ctx = ClientContext(sp_url, ctx_auth)
folder = ctx.web.get_folder_by_server_relative_url(sp_path)
files = folder.files
ctx.load(files)
ctx.execute_query()

# Process each file
for file in files:
    name = file.properties["Name"]
    print(name)

    if name.endswith(".json"):
        file_url = file.properties["ServerRelativeUrl"]
        file_bytes = File.open_binary(ctx, file_url).content
        file_stream = io.BytesIO(file_bytes)

        try:
            data = json.load(file_stream)
        except:
            file_stream.seek(0)
            data = json.loads(file_stream.read().decode("utf-8"))

        df = pd.json_normalize(data)

        if name == "sales_dimensions.json":
            # region_dimension
            region_cols = ["region_id", "region_name", "region_country", "regional_manager"]
            region_df = df[region_cols].drop_duplicates()
            region_df = region_df[region_df["region_id"].notnull()]
            region_df = region_df.drop_duplicates(subset=["region_id"])
            region_df.to_sql("region_dimension", engine, if_exists="replace", index=False)
            print(f" region_dimension loaded ({len(region_df)} rows)")

            # promotion_dimension
            promo_cols = ["promotion_id", "promotion_name", "discount_percentage", "start_date", "end_date"]
            promo_df = df[promo_cols].drop_duplicates()
            promo_df = promo_df[promo_df["promotion_id"].notnull()]
            promo_df = promo_df.drop_duplicates(subset=["promotion_id"])
            promo_df.to_sql("promotion_dimension", engine, if_exists="replace", index=False)
            print(f" promotion_dimension loaded ({len(promo_df)} rows)")

            # sales_dimensions
            sales_cols = [
                "supplier_id", "supplier_name", "contact_email", "supplier_country",
                "reliability_score", "region_id", "promotion_id"
            ]
            sales_df = df[sales_cols]
            sales_df = sales_df[sales_df["supplier_id"].notnull()]
            sales_df = sales_df.drop_duplicates(subset=["supplier_id"])
            sales_df.to_sql("sales_dimensions", engine, if_exists="replace", index=False)
            print(f"sales_dimensions loaded ({len(sales_df)} rows)")

        else:
            table_name = os.path.splitext(name)[0]

            # Clean PK if defined
            if table_name in primary_keys:
                pk_col = primary_keys[table_name]
                null_count = df[pk_col].isnull().sum()
                dup_count = df[pk_col].duplicated().sum()

                if null_count > 0:
                    print(f" {table_name}.{pk_col} has {null_count} NULLs. Removing...")
                    df = df[df[pk_col].notnull()]

                if dup_count > 0:
                    print(f"{table_name}.{pk_col} has {dup_count} duplicate values. Removing...")
                    df = df.drop_duplicates(subset=[pk_col])

            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f" {table_name} loaded ({len(df)} rows)")

# Apply Primary Keys
with engine.connect() as conn:
    for table, pk in primary_keys.items():
        try:
            conn.execute(text(f"""
                ALTER TABLE {table}
                ADD CONSTRAINT PK_{table} PRIMARY KEY ({pk})
            """))
            print(f"PK applied: {table}.{pk}")
        except Exception as e:
            print(f" Could not apply PK on {table}: {e}")

# Apply Foreign Keys
with engine.connect() as conn:
    for table, fks in foreign_keys.items():
        for col, ref_table, ref_col in fks:
            try:
                fk_name = f"FK_{table}_{col}"
                conn.execute(text(f"""
                    ALTER TABLE {table}
                    ADD CONSTRAINT {fk_name}
                    FOREIGN KEY ({col})
                    REFERENCES {ref_table}({ref_col})
                """))
                print(f" FK applied: {table}.{col} → {ref_table}.{ref_col}")
            except Exception as e:
                print(f" Could not apply FK {table}.{col}: {e}")
