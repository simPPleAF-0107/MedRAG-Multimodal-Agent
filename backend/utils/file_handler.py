import os
import shutil
from fastapi import UploadFile

class FileHandler:
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_upload_file(self, upload_file: UploadFile) -> str:
        """
        Saves an uploaded file to the local disk and returns the path.
        """
        file_path = os.path.join(self.upload_dir, upload_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path

    def delete_local_file(self, file_path: str):
        """
        Deletes a locally saved file.
        """
        if os.path.exists(file_path):
            os.remove(file_path)

file_handler = FileHandler()
