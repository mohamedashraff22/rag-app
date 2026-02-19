from enum import Enum


class ResponseSignal(Enum):
    FILE_VALITADED_SUCCESS = "File validated successfully."
    FILE_TYPE_NOT_SUPPORTED = "File type not allowed."
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum allowed size."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_UPLOADED_FAILED = "File upload failed."
    PROCESSING_FAILED = "Processing failed."
    PROCESSING_SUCCESS = "Processing successfully."
    NO_FILES_ERROR = "No files found in the project."
    FILE_ID_ERROR = "no file found with this id "
