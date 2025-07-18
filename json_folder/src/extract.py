import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File  # ✅ Correct import
from config.settings import SHAREPOINT_SITE_URL, SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD


def download_json_files(destination_folder):
    ctx = ClientContext(SHAREPOINT_SITE_URL).with_credentials(
        UserCredential(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
    )

    folder_url = "/sites/kasmo-training/Shared Documents/DATASET/JSON_FILES"
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    files = folder.files.get().execute_query()

    os.makedirs(destination_folder, exist_ok=True)

    for f in files:
        if f.name.endswith(".json"):
            response = File.open_binary(ctx, f.serverRelativeUrl)
            file_path = os.path.join(destination_folder, f.name)
            with open(file_path, "wb") as out_file:
                out_file.write(response.content)

    print("✅ JSON files downloaded from SharePoint.")
