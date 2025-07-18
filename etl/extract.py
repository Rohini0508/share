# etl/extract.py

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from config.settings import SHAREPOINT_SITE_URL, SHAREPOINT_LIST_NAME, USERNAME, PASSWORD
import json
import os

def extract_data():
    # Authenticate
    ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
    if not ctx_auth.acquire_token_for_user(USERNAME, PASSWORD):
        raise Exception("SharePoint authentication failed")

    # Connect to SharePoint list
    ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)
    sp_list = ctx.web.lists.get_by_title(SHAREPOINT_LIST_NAME)
    items = sp_list.items.get().execute_query()

    # Extract raw item properties
    data = [item.properties for item in items]

    # ✅ Robust serializer: convert all non-JSON-native objects to strings
    def make_json_safe(obj):
        if isinstance(obj, dict):
            return {k: make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_json_safe(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)  # fallback to string

    json_safe_data = [make_json_safe(item) for item in data]

    # Save for debugging (optional)
    os.makedirs("data", exist_ok=True)
    with open("data/extracted_data.json", "w") as f:
        json.dump(json_safe_data, f, indent=4)

    return data
