# config/settings.py

# SharePoint Settings
SHAREPOINT_SITE_URL = "https://kasmoco.sharepoint.com/sites/kasmo-training/"
SHAREPOINT_FOLDER_PATH = "/sites/kasmo-training/Shared Documents/DATASET/JSON_FILES"

# Use UserCredential (username and password for login)
SHAREPOINT_CLIENT_ID = "rohini.panguluri@kasmodigital.com"
SHAREPOINT_CLIENT_SECRET = "Tharun9014455731" 


# config/settings.py

SHAREPOINT_SITE_URL = "https://kasmoco.sharepoint.com/sites/kasmo-training/"
SHAREPOINT_USERNAME = "rohini.panguluri@kasmodigital.com"
SHAREPOINT_PASSWORD = "Tharun9014455731" 


# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "etl_project"
MONGO_COLLECTION_NAME = "raw_json_data"

# SQL Server Configuration
SQL_CONFIG = {
    "DRIVER": "ODBC Driver 17 for SQL Server",
    "SERVER": "DESKTOP-D933C06\SQLEXPRESS",   # Double backslashes for escape
    "DATABASE": "Rohini",
    "USERNAME": "sa",
    "PASSWORD": "tharun"
}
