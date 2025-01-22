import logging
import traceback
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, APIRouter

import crud
from config import auth_schema
from utils import check_product
from database import get_session

router = APIRouter()


class Product(BaseModel):
    article: int


@router.post('/')
async def save_product(product: Product, user: str = Depends(auth_schema), db: AsyncSession = Depends(get_session)):
    article_info = await check_product(product.article)

    if isinstance(article_info, HTTPException):
        raise article_info

    try:
        await crud.save_product(article_info, db)
        return HTTPException(status_code=200, detail='Товар успешно сохранен')
    except Exception:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='Ошибка при сохранении товара')


@router.get('/subscribe/{article}')
async def tracking_product(article: int, user: str = Depends(auth_schema), db: AsyncSession = Depends(get_session)):
    await save_product(Product(article=article), user, db)
    try:
        await crud.tracked_product(article, db)
        return HTTPException(status_code=200, detail='Товар успешно добавлен в отслеживание')
    except Exception:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='Ошибка при добавление товара в отслеживание')
