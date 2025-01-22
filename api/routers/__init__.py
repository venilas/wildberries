from fastapi import FastAPI

from . import product, auth


def on_startup_routers(app: FastAPI) -> None:
    app.include_router(product.router, prefix='/api/v1/products', tags=['products'])
    app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
