from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os
import re
from .ProjectController import ProjectController


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scaled = 1048576  # 1 MB in bytes (1024 * 1024)

    def validate_uploaded_file(self, file: UploadFile):

        if (
            file.content_type not in self.app_settings.FILE_ALLOWED_TYPES
        ):  # .content type will return the real type of the file (ex: text/plain for txt files and application/pdf for pdf files) not just the extentton
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if (
            file.size > self.app_settings.FILE_MAX_SIZE * self.size_scaled
        ):  # convert the max size from MB to bytes
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALITADED_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):

        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)

        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r"[^\w.]", "", orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
