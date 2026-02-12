from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",  # set the prefix for all routes in this router (empty means no prefix)
    tags=[
        "api_v1"
    ],  # set the tags for all routes in this router (used for documentation purposes
)


@base_router.get("/")  # define a GET endpoint at the root URL
async def welcome():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    return {"App Name": app_name, "App Version": app_version}
