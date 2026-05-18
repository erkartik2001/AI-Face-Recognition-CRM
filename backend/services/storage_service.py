import os
from dotenv import load_dotenv

from b2sdk.v2 import InMemoryAccountInfo
from b2sdk.v2 import B2Api

import requests


load_dotenv()


class B2Storage:

    def __init__(self):

        self.key_id = os.getenv("B2_KEY_ID")
        self.application_key = os.getenv("B2_APPLICATION_KEY")
        self.bucket_name = os.getenv("B2_BUCKET_NAME")

        # Initialize B2 API
        info = InMemoryAccountInfo()

        self.b2_api = B2Api(info)

        self.b2_api.authorize_account(
            "production",
            self.key_id,
            self.application_key
        )

        # Get bucket
        self.bucket = self.b2_api.get_bucket_by_name(
            self.bucket_name
        )

        print("Backblaze B2 Connected")


    def upload_file(
        self,
        local_file_path,
        b2_file_name
    ):

        uploaded_file = self.bucket.upload_local_file(
            local_file=local_file_path,
            file_name=b2_file_name
        )

        file_url = (
            f"https://f005.backblazeb2.com/file/"
            f"{self.bucket_name}/{b2_file_name}"
        )

        return {
            "file_name": b2_file_name,
            "file_url": file_url
        }


    def list_files(self):

        files = []

        for file_version, folder_name in self.bucket.ls():

            file_name = file_version.file_name

            file_url = (
                f"https://f005.backblazeb2.com/file/"
                f"{self.bucket_name}/{file_name}"
            )

            files.append({
                "file_name": file_name,
                "file_url": file_url
            })

        return files
    
    def download_file(
        self,
        file_url,
        save_path
    ):

        response = requests.get(file_url)

        if response.status_code == 200:

            with open(save_path, "wb") as f:
                f.write(response.content)

            return save_path

        else:
            raise Exception(
                f"Failed to download file: {file_url}"
            )
