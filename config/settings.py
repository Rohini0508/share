# config/settings.py

SHAREPOINT_SITE_URL = "https://kasmoco.sharepoint.com/sites/kasmo-training"
SHAREPOINT_LIST_NAME = "Projects"  # Must match the list name in SharePoint

USERNAME = "rohini.panguluri@kasmodigital.com"
PASSWORD = "Tharun9014455731"  #M@n!$#@143 M@n!$#@143

SQL_CONFIG = {
    "DRIVER": "ODBC Driver 17 for SQL Server",
    "SERVER": r"DESKTOP-D933C06\SQLEXPRESS",  # Use raw string for backslash
    "DATABASE": "Rohini",
    "USERNAME": "sa",
    "PASSWORD": "tharun"  # ✅ fixed typo
}
