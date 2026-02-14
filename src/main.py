from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings


app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    # the data i will atach to the whole application
    settings = get_settings()
    # in routes they will see it
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DATABASE]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_conn.close()


app.include_router(base.base_router)  # include the base router in the main application
app.include_router(data.data_router)  # include the data router in the main application
