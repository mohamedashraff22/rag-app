from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",  # set the prefix for all routes in this router (empty means no prefix)
    tags=[
        "api_v1"
    ],  # set the tags for all routes in this router (used for documentation purposes
)


@base_router.get("/")  # define a GET endpoint at the root URL
async def welcome(
    app_settings: Settings = Depends(get_settings),
):  # use Depends to inject the settings instance into the endpoint function
    # app_settings = get_settings() # get the settings instance to access configuration variables

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {"App Name": app_name, "App Version": app_version}
