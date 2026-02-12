from fastapi import FastAPI
from routes import base

app = FastAPI()
app.include_router(base.base_router)  # include the base router in the main application
