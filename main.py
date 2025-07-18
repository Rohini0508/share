# main.py
import logging
from etl.extract import extract_data
from etl.tansform import transform_data
from etl.load import load_data

logging.basicConfig(filename='logs/etl.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def run_etl():
    try:
        logging.info("ETL process started")
        raw = extract_data()
        logging.info("Extraction complete")

        transformed = transform_data(raw)
        logging.info("Transformation complete")

        load_data(transformed)
        logging.info("Data successfully loaded into SQL Server")

    except Exception as e:
        logging.error(f"ETL failed: {e}")

if __name__ == "__main__":
    run_etl()
