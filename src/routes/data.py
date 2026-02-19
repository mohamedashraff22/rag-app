from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import (
    DataController,
    ProjectController,
    ProcessController,
)  # i used the init (in controller directory) not to import the controller directly but to make it available for import from the controllers package (i will use it in the routes to call the validation function for the uploaded file)
import os
import aiofiles
from models import ResponseSignal
import logging
from .schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk, Asset
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum


logger = logging.getLogger("uvicorn.error")


data_router = APIRouter(
    prefix="/api/v1/data",  # set the prefix for all routes in this router (empty means no prefix)
    tags=[
        "api_v1",
        "data",
    ],  # set the tags for all routes in this router (used for documentation purposes
)


@data_router.post("/upload/{project_id}")  # define a POST endpoint at the /upload URL
async def upload_data(
    request: Request,  # request = Request -> get all the information about the request coming to me inclued the app in the main as i want to access the db connection which is in the main
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):

    # instead of "project_model = ProjectModel(db_client=request.app.db_client)"
    # as create_instance is asynchronous function, it must be called with await
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_one(project_id=project_id)

    # validate the file properties (i will do it in controllers (separtate logic from routes))
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"signal": result_signal}
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename, project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNCK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_UPLOADED_FAILED.value},
        )

    # store the assets into the database
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(
                asset_record.id
            ),  # as it returns object from mongo so in python we neet to turn it to string
        }
    )


# giving file_id will be now optional, if i give it process it, if its None scan all files in this project and process them.
@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request, project_id: str, process_request: ProcessRequest
):
    file_id = process_request.file_id
    chunck_size = process_request.chunk_size
    chunck_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_one(project_id=project_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    project_files_ids = {}
    if process_request.file_id:  # given one file (note none)
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id, asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.FILE_ID_ERROR.value},
            )

        project_files_ids = {asset_record.id: asset_record.asset_name}

    else:  # None , no give file
        # so now i will got all project file from the "asset model"
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id, asset_type=AssetTypeEnum.FILE.value
        )  # now i have all the files in the collection, and i wnat to get the asset_id (file_id) , so i will iterate on them

        project_files_ids = {record.id: record.asset_name for record in project_files}

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.NO_FILES_ERROR.value},
        )

    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    # loop over all files (either they are given id (just one file), or more)
    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunck_size,
            chunk_overlap=chunck_overlap,
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            )

        # i want to turn evry chunk to object of DataChunk
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,  # problem of _id -> as underscore for the pydantic means this is private (we access it with id , _id only use in mongo)
                chunk_asset_id=asset_id,
            )
            # enamurate is a normal loop that loops over list of elemtns , but it returns the element with its order
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "proecessed_files": no_files,
        }
    )
