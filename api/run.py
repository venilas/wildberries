import asyncio

from fastapi import FastAPI

from database import init_models
from routers import on_startup_routers
from crud import update_tracked_products

app = FastAPI()


asyncio.create_task(init_models())
asyncio.create_task(update_tracked_products())
on_startup_routers(app)
