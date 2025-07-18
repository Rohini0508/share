# load/load_to_mongodb.py

import os, json
from pymongo import MongoClient
from config.settings import MONGO_URI

def load_to_mongodb(json_folder):
    client = MongoClient(MONGO_URI)
    db = client["SharePointDB"]
    collection = db["CustomerRaw"]

    for file in os.listdir(json_folder):
        if file.endswith(".json"):
            with open(os.path.join(json_folder, file)) as f:
                data = json.load(f)
                if isinstance(data, list):
                    collection.insert_many(data)
                else:
                    collection.insert_one(data)

    print("✅ JSON data loaded into MongoDB.")
