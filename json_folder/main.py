# main.py

from src.extract import download_json_files
from src.load import load_to_mongodb
from src.trans import transform_and_load

def run_etl():
    print("🚀 ETL Started...")
    download_json_files("json_files")
    load_to_mongodb("json_files")
    transform_and_load()
    print("✅ ETL Process Completed.")

if __name__ == "__main__":
    run_etl()
